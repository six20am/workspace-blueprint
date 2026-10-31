#!/usr/bin/env python3
"""photo-organizer: rename photos and videos by the date taken, set exact duplicates aside,
and sort everything into YEAR/MONTH folders inside one folder the person names.

Safety:
  - A dry run is the default. Nothing moves until --apply is given.
  - Nothing is ever deleted. Duplicates are moved to <folder>/duplicates/.
  - Every move stays inside the folder given with --root.
  - An --apply run writes an undo CSV beside the folder; --undo <csv> --apply puts every file back.
  - No network. Standard library only.

Usage:
  python organize.py --root "<folder>"                 # dry run: print the plan, move nothing
  python organize.py --root "<folder>" --apply         # do it and write the undo CSV
  python organize.py --undo "<undo csv>"               # preview the undo
  python organize.py --undo "<undo csv>" --apply       # put every file back
Options: --keep-name (keep the old name in front of the date), --skip-mtime (leave files
whose only date is the file's modified time where they are), --no-dedupe.
"""
import argparse
import csv
import datetime
import hashlib
import os
import re
import shutil
import struct
import sys
from collections import Counter, defaultdict

IMG = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff', '.webp', '.heic', '.heif', '.dng'}
VID = {'.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', '.3gp', '.mpg', '.mpeg', '.ts'}
MP4_LIKE = {'.mp4', '.mov', '.m4v', '.3gp'}
SIDECAR = {'.aae', '.xmp', '.thm'}  # follow the photo with the same name

DUP_DIR = 'duplicates'
DSRC_RANK = {'exif': 0, 'video': 1, 'filename': 2, 'mtime': 3}
DSRC_TEXT = {'exif': 'photo EXIF', 'video': 'video metadata', 'filename': 'file name',
             'mtime': 'file modified time, may be the copy date'}
FIELDS = ['step', 'status', 'old_path', 'new_path', 'date', 'date_source', 'root', 'detail']


# ---------- EXIF / TIFF ----------
TYPE_SIZE = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8, 13: 4}


def read_ifd(tiff, off, u16, u32):
    """Return {tag: (type, count, value offset)}. Values of 4 bytes or less sit inside the entry."""
    tags = {}
    try:
        cnt = u16(off)
    except struct.error:
        return tags
    if cnt > 1000:
        return tags
    for k in range(cnt):
        eo = off + 2 + k * 12
        if eo + 12 > len(tiff):
            break
        tag, typ, n = u16(eo), u16(eo + 2), u32(eo + 4)
        size = TYPE_SIZE.get(typ, 1) * n
        tags[tag] = (typ, n, eo + 8 if size <= 4 else u32(eo + 8))
    return tags


def parse_tiff(tiff):
    """Read the date taken from a TIFF/EXIF block. Return a datetime or None."""
    if len(tiff) < 8 or tiff[:2] not in (b'II', b'MM'):
        return None
    e = '>' if tiff[:2] == b'MM' else '<'
    u16 = lambda o: struct.unpack(e + 'H', tiff[o:o + 2])[0]
    u32 = lambda o: struct.unpack(e + 'I', tiff[o:o + 4])[0]
    try:
        if u16(2) != 0x002A:  # 0x002A sits at offset 2; offset 0 is the byte order
            return None
        ifd0 = read_ifd(tiff, u32(4), u16, u32)

        def text(tags, tag):
            if tag not in tags:
                return None
            _, n, vo = tags[tag]
            s = tiff[vo:vo + n].split(b'\x00')[0].decode('utf-8', 'ignore').strip()
            return s or None

        exif = {}
        if 0x8769 in ifd0:
            exif = read_ifd(tiff, u32(ifd0[0x8769][2]), u16, u32)
        # DateTimeOriginal, then DateTimeDigitized (Exif sub-IFD), then DateTime (IFD0, often the edit time)
        for tags, tag in ((exif, 0x9003), (exif, 0x9004), (ifd0, 0x0132)):
            s = text(tags, tag)
            if s and re.match(r'^\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}', s):
                try:
                    return datetime.datetime.strptime(s[:19], '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    pass
        return None
    except (struct.error, IndexError):
        return None


def jpeg_exif_block(head):
    i, n = 2, len(head)
    while i + 4 <= n:
        if head[i] != 0xFF:
            break
        m = head[i + 1]
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        if m == 0xDA:
            break
        sl = int.from_bytes(head[i + 2:i + 4], 'big')
        if m == 0xE1 and head[i + 4:i + 10] == b'Exif\x00\x00':
            return head[i + 10:i + 2 + sl]
        i += 2 + sl
    return None


def embedded_tiff(buf):
    """Find the EXIF TIFF block inside HEIC, WebP or PNG."""
    for marker in (b'Exif\x00\x00II*\x00', b'Exif\x00\x00MM\x00*'):
        k = buf.find(marker)
        if k >= 0:
            return buf[k + 6:]
    k = buf.find(b'eXIf')  # PNG eXIf chunk: the data is TIFF directly
    if k >= 0 and buf[k + 4:k + 6] in (b'II', b'MM'):
        return buf[k + 4:]
    return None


def exif_date(path, ext):
    try:
        with open(path, 'rb') as f:
            head = f.read(2 * 1024 * 1024 if ext in ('.heic', '.heif') else 512 * 1024)
    except OSError:
        return None
    if head[:2] == b'\xff\xd8':
        tiff = jpeg_exif_block(head)
    elif head[:4] in (b'II*\x00', b'MM\x00*'):  # TIFF and DNG are TIFF already
        tiff = head
    else:
        tiff = embedded_tiff(head)
    return parse_tiff(tiff) if tiff else None


# ---------- video creation time (MP4/MOV mvhd) ----------
MAC_EPOCH = 2082844800  # seconds from 1904-01-01 to 1970-01-01


def video_created(path):
    try:
        with open(path, 'rb') as f:
            total = os.fstat(f.fileno()).st_size
            pos = 0
            while pos + 8 <= total:
                f.seek(pos)
                sz, typ = struct.unpack('>I4s', f.read(8))
                hl = 8
                if sz == 1:
                    sz, hl = struct.unpack('>Q', f.read(8))[0], 16
                elif sz == 0:
                    sz = total - pos
                if sz < hl:
                    break
                if typ == b'moov':
                    data = f.read(min(sz - hl, 64 << 20))
                    k = data.find(b'mvhd')
                    if k < 0:
                        return None
                    if data[k + 4] == 1:
                        secs = struct.unpack('>Q', data[k + 8:k + 16])[0]
                    else:
                        secs = struct.unpack('>I', data[k + 8:k + 12])[0]
                    if secs < MAC_EPOCH + 86400 * 365:  # zero or before 1971 means not filled in
                        return None
                    return datetime.datetime.fromtimestamp(secs - MAC_EPOCH)  # mvhd is UTC; show local time
                pos += sz
    except (OSError, struct.error, IndexError, OverflowError, ValueError):
        pass
    return None


# ---------- dates in file names ----------
FN_SEP = re.compile(r'(?<!\d)((?:19|20)\d{2})[-_.](\d{1,2})[-_.](\d{1,2})[ _T.-](\d{2})[-_.:]?(\d{2})[-_.:]?(\d{2})(?!\d)')
FN_COMPACT = re.compile(r'(?<!\d)((?:19|20)\d{2})(\d{2})(\d{2})[ _T-]?(\d{2})(\d{2})(\d{2})(?!\d)')
FN_EPOCH = re.compile(r'(?:mmexport|wx_camera_)(\d{13})', re.I)


def filename_date(name):
    now = datetime.datetime.now()
    for rx in (FN_SEP, FN_COMPACT):
        m = rx.search(name)
        if m:
            try:
                dt = datetime.datetime(*map(int, m.groups()))
                if 1990 <= dt.year <= now.year + 1:
                    return dt
            except ValueError:
                pass
    m = FN_EPOCH.search(name)
    if m:
        try:
            dt = datetime.datetime.fromtimestamp(int(m.group(1)) / 1000)
            if 2010 <= dt.year <= now.year + 1:
                return dt
        except (OverflowError, OSError, ValueError):
            pass
    return None


# ---------- file info ----------
class FileInfo:
    __slots__ = ('path', 'ext', 'size', 'mtime', 'dt', 'dsrc')

    @property
    def stem(self):
        return os.path.splitext(os.path.basename(self.path))[0]


def probe(path):
    f = FileInfo()
    f.path = path
    f.ext = os.path.splitext(path)[1].lower()
    st = os.stat(path)
    f.size, f.mtime = st.st_size, st.st_mtime
    f.dt = f.dsrc = None
    if f.ext in IMG:
        dt = exif_date(path, f.ext)
        if dt:
            f.dt, f.dsrc = dt, 'exif'
    elif f.ext in MP4_LIKE:
        dt = video_created(path)
        if dt:
            f.dt, f.dsrc = dt, 'video'
    if f.dt is None:
        dt = filename_date(os.path.basename(path))
        if dt:
            f.dt, f.dsrc = dt, 'filename'
    if f.dt is None:
        f.dt, f.dsrc = datetime.datetime.fromtimestamp(f.mtime).replace(microsecond=0), 'mtime'
    return f


def collect(root):
    """Walk the folder for photos and videos, skipping the top-level duplicates/. Return (files, sidecars)."""
    files, sidecars = [], defaultdict(list)
    for dp, dirs, fs in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not (nc(dp) == nc(root) and d.lower() == DUP_DIR))
        for fn in sorted(fs):
            ext = os.path.splitext(fn)[1].lower()
            p = os.path.join(dp, fn)
            if ext in IMG or ext in VID:
                try:
                    files.append(probe(p))
                except OSError:
                    continue
            elif ext in SIDECAR:
                sidecars[(dp, os.path.splitext(fn)[0].lower())].append(p)
    return files, sidecars


# ---------- planning ----------
def nc(p):
    return os.path.normcase(os.path.abspath(p))


def inside(root, p):
    try:
        return os.path.commonpath([nc(root), nc(p)]) == nc(root)
    except ValueError:  # different drives
        return False


class Reserver:
    """Hold target paths so two files in one plan never get the same name."""

    def __init__(self):
        self.taken = set()

    def free(self, path, src=None):
        if src is not None and nc(path) == nc(src):
            return True
        return nc(path) not in self.taken and not os.path.exists(path)

    def take(self, path):
        self.taken.add(nc(path))
        return path

    def unique(self, path):
        base, ext = os.path.splitext(path)
        n = 1
        while not self.free(path):
            n += 1
            path = f'{base}_{n}{ext}'
        return self.take(path)


def action(step, src, dst, f=None, detail='', status='planned', root=''):
    return {'step': step, 'status': status, 'old_path': src, 'new_path': dst,
            'date': f.dt.isoformat(' ') if f else '', 'date_source': f.dsrc if f else '',
            'root': root, 'detail': detail}


COPY_RE = re.compile(r'copy|\(\d+\)', re.I)


def file_hash(path, limit=None):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        if limit:
            h.update(fh.read(limit))
        else:
            for chunk in iter(lambda: fh.read(1 << 20), b''):
                h.update(chunk)
    return h.hexdigest()


def group_by(items, key):
    d = defaultdict(list)
    for it in items:
        try:
            d[key(it)].append(it)
        except OSError:
            pass
    return [g for g in d.values() if len(g) > 1]


def exact_dup_groups(files):
    """Same size, then same SHA-256 of the first 64 KB, then same SHA-256 of the whole file."""
    out = []
    for g1 in group_by([f for f in files if f.size > 0], lambda f: f.size):
        for g2 in group_by(g1, lambda f: file_hash(f.path, 65536)):
            if g2[0].size <= 65536:
                out.append(g2)
            else:
                out.extend(group_by(g2, lambda f: file_hash(f.path)))
    return out


def keep_key(f):
    # name does not look like a copy, then shallower folder, then older, then shorter name
    return (bool(COPY_RE.search(os.path.basename(f.path))), f.path.count(os.sep), f.mtime,
            len(os.path.basename(f.path)), f.path)


def plan_dedupe(files, root, res):
    acts = []
    for g in exact_dup_groups(files):
        g.sort(key=keep_key)
        keep = g[0]
        for f in g[1:]:
            dst = res.unique(os.path.join(root, DUP_DIR, os.path.relpath(f.path, root)))
            acts.append(action('duplicate', f.path, dst, f,
                               'same bytes as ' + os.path.relpath(keep.path, root), root=root))
    return acts


OUR_NAME = re.compile(r'^(.*?)_?\d{4}-\d{1,2}-\d{1,2}_\d{6}(?:_\d+)?$')


def date_name(dt):
    return f'{dt.year}-{dt.month:02d}-{dt.day:02d}_{dt.hour:02d}{dt.minute:02d}{dt.second:02d}'


def strip_our_suffix(stem):
    """On a second run, drop the date this tool added last time so names do not grow."""
    m = OUR_NAME.match(stem)
    return m.group(1) if m else stem


def stem_groups(files, sidecars):
    """Files in one folder with one name (a HEIC photo and its MOV clip, RAW and JPG, an .AAE) move together."""
    groups = defaultdict(list)
    for f in files:
        groups[(os.path.dirname(f.path), f.stem.lower())].append(f)
    out = []
    for key in sorted(groups):
        members = groups[key]
        best = min(members, key=lambda f: DSRC_RANK[f.dsrc])
        out.append((members, sidecars.get(key, []), best))
    return out


def plan_organize(files, root, res, sidecars, keep_name=False, skip_mtime=False):
    acts = []
    for members, extra, best in stem_groups(files, sidecars):
        if best.dsrc == 'mtime' and skip_mtime:
            for m in members:
                acts.append(action('organize', m.path, '', best, 'left in place: only a file modified time',
                                   status='kept', root=root))
            continue
        tdir = os.path.join(root, f'{best.dt.year}', f'{best.dt.month:02d}')
        base = date_name(best.dt)
        if keep_name:
            old = strip_our_suffix(best.stem)
            base = f'{old}_{base}' if old else base
        paths = [m.path for m in members] + extra
        n = 1
        while True:
            name = base + (f'_{n}' if n > 1 else '')
            targets = [os.path.join(tdir, name + os.path.splitext(p)[1]) for p in paths]
            if all(res.free(t, p) for t, p in zip(targets, paths)):
                break
            n += 1
        for t, p in zip(targets, paths):
            res.take(t)
            if os.path.abspath(t) != os.path.abspath(p):
                acts.append(action('organize', p, t, best, root=root))
    return acts


# ---------- doing it ----------
def move(src, dst, root):
    if not (inside(root, src) and inside(root, dst)):
        raise PermissionError(f'outside the folder: {dst}')
    if os.path.exists(dst) and nc(src) != nc(dst):
        raise FileExistsError(f'already exists: {dst}')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if nc(src) == nc(dst):
        os.rename(src, dst)  # a change of letter case only
    else:
        shutil.move(src, dst)


def write_csv(path, acts):
    with open(path, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(acts)


def undo_csv_path(root):
    """The undo file sits beside the folder, so sorting the folder never touches it."""
    parent = os.path.dirname(root)
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    name = os.path.basename(root) or 'photos'
    where = parent if parent and nc(parent) != nc(root) else root
    path = os.path.join(where, f'{name}-photo-organizer-undo-{ts}.csv')
    n = 1
    while os.path.exists(path):
        n += 1
        path = os.path.join(where, f'{name}-photo-organizer-undo-{ts}-{n}.csv')
    return path


def show(root, acts, limit):
    shown = 0
    for title, step in (('Duplicates (moved to duplicates/, nothing deleted):', 'duplicate'),
                        ('Rename and sort into year and month folders:', 'organize')):
        rows = [a for a in acts if a['step'] == step]
        if not rows:
            continue
        print(title)
        for a in rows:
            if shown >= limit:
                break
            shown += 1
            src = os.path.relpath(a['old_path'], root)
            dst = os.path.relpath(a['new_path'], root) if a['new_path'] else '(stays where it is)'
            if step == 'duplicate':
                note = a['detail']
            else:
                note = 'date from: ' + DSRC_TEXT[a['date_source']]
                if a['detail']:
                    note += '; ' + a['detail']
            print(f'  {src}  ->  {dst}   [{note}]')
    if len(acts) > shown:
        print(f'  ...and {len(acts) - shown} more')


def cmd_organize(args):
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        sys.exit(f'Folder not found: {root}')
    files, sidecars = collect(root)
    res = Reserver()
    dup = [] if args.no_dedupe else plan_dedupe(files, root, res)
    gone = {nc(a['old_path']) for a in dup}
    rest = [f for f in files if nc(f.path) not in gone]
    org = plan_organize(rest, root, res, sidecars, args.keep_name, args.skip_mtime)
    acts = dup + org
    print(('APPLY: moving files now.' if args.apply else 'DRY RUN: nothing will move.') + f' Folder: {root}')
    vids = sum(1 for f in files if f.ext in VID)
    print(f'Found {len(files)} media files ({len(files) - vids} photos, {vids} videos), {len(dup)} duplicates.\n')
    if not acts:
        print('Nothing to do: every file is already named and sorted.')
        return
    show(root, acts, args.limit)
    ds = Counter(f.dsrc for f in rest)
    print('\nDate sources: ' + ', '.join(f'{DSRC_TEXT[k].split(",")[0]} {ds[k]}' for k in DSRC_RANK if ds[k]))
    if ds['mtime']:
        print(f'{ds["mtime"]} file(s) have no date inside them; their file modified time was used'
              + (' only to report it; they stay where they are (--skip-mtime).' if args.skip_mtime else '.'))
    if not args.apply:
        print('\nThis was a dry run. To do it, run the same command with --apply.')
        return
    log = undo_csv_path(root)
    write_csv(log, acts)  # written first, so an interrupted run can still be undone
    try:
        for a in acts:
            if a['status'] != 'planned':
                continue
            try:
                move(a['old_path'], a['new_path'], root)
                a['status'] = 'done'
            except OSError as e:
                a['status'], a['detail'] = 'failed', f'{a["detail"]} | {e}'.strip(' |')
    finally:
        write_csv(log, acts)
    done = sum(1 for a in acts if a['status'] == 'done')
    failed = sum(1 for a in acts if a['status'] == 'failed')
    print(f'\nMoved {done} file(s). Failed: {failed}.' + (' See the detail column in the undo file.' if failed else ''))
    print(f'Undo file: {log}')
    print(f'To undo: python "{os.path.abspath(__file__)}" --undo "{log}" --apply')


def remove_empty_dirs(path, root):
    """After an undo, remove folders it left empty, up to the root. rmdir refuses a folder with anything in it."""
    p = os.path.dirname(os.path.abspath(path))
    while inside(root, p) and nc(p) != nc(root):
        try:
            os.rmdir(p)
        except OSError:
            return
        p = os.path.dirname(p)


def cmd_undo(args):
    if not os.path.isfile(args.undo):
        sys.exit(f'Undo file not found: {args.undo}')
    with open(args.undo, newline='', encoding='utf-8-sig') as fh:
        rows = [r for r in csv.DictReader(fh) if r.get('status') in ('done', 'planned') and r.get('new_path')]
    if not rows:
        print('Nothing in this file to undo.')
        return
    results = Counter()
    print('UNDO: moving files back.' if args.apply else 'UNDO PREVIEW: nothing will move.')
    for r in reversed(rows):
        new, old, root = r['new_path'], r['old_path'], r.get('root') or ''
        if not root or not (inside(root, new) and inside(root, old)):
            status = 'skipped: path outside the organized folder'
        elif not os.path.exists(new):
            status = 'skipped: not found where it was moved' if r['status'] == 'done' else 'skipped: never moved'
        elif os.path.exists(old) and nc(old) != nc(new):
            status = 'skipped: a file is already at the original path'
        elif args.apply:
            try:
                move(new, old, root)
                remove_empty_dirs(new, root)
                status = 'restored'
            except OSError as e:
                status = f'failed: {e}'
        else:
            status = 'will restore'
        results[status.split(':')[0]] += 1
        print(f'  {new}  ->  {old}   [{status}]')
    print('\n' + ', '.join(f'{k}: {v}' for k, v in results.items()))
    if not args.apply:
        print('This was a preview. To put the files back, run the same command with --apply.')


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors='replace')
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description='Rename photos by date taken, set duplicates aside, sort by year '
                                             'and month. Dry run unless --apply. Never deletes.')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--root', help='the folder to organize (subfolders included)')
    g.add_argument('--undo', help='an undo CSV written by an --apply run')
    ap.add_argument('--apply', action='store_true', help='actually move files (default: dry run)')
    ap.add_argument('--keep-name', action='store_true', help='keep the old name in front of the date')
    ap.add_argument('--skip-mtime', action='store_true', help='leave files whose only date is the modified time')
    ap.add_argument('--no-dedupe', action='store_true', help='do not look for duplicates')
    ap.add_argument('--limit', type=int, default=200, help='most plan lines to print (default 200)')
    args = ap.parse_args(argv)
    if args.undo:
        cmd_undo(args)
    else:
        cmd_organize(args)


if __name__ == '__main__':
    main()
