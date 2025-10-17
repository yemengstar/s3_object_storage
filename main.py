"""
S3-compatible Object Storage Uploader (Tkinter GUI)

Features:
- Configure custom S3 endpoint, access key, secret key, bucket, and base URL for public links
- Select multiple files (Add / Remove)
- Upload files in background threads with per-file progress
- Generate shareable URLs and copy to clipboard
- Simple logs and status

Requirements:
- Python 3.8+
- boto3
- botocore
- pyperclip (optional, falls back to Tk clipboard)

Usage:
python s3_uploader_gui.py

"""
import threading
import os
import mimetypes
import queue
import time
from pathlib import Path
from tkinter import (
    Tk, Frame, Label, Entry, Button, Listbox, Scrollbar, END, SINGLE,
    filedialog, StringVar, IntVar, Checkbutton, ttk, Text, VERTICAL, HORIZONTAL, BOTH, LEFT, RIGHT, Y
)
from tkinter.scrolledtext import ScrolledText

try:
    import boto3
    from botocore.config import Config
    from boto3.s3.transfer import TransferConfig
except Exception as e:
    raise ImportError('This program requires boto3 and botocore. Install with: pip install boto3')

try:
    import pyperclip
    HAVE_PYPERCLIP = True
except Exception:
    HAVE_PYPERCLIP = False


class ProgressPercentage(object):
    def __init__(self, filename, filesize, update_fn):
        self._filename = filename
        self._size = filesize
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._update_fn = update_fn

    def __call__(self, bytes_amount):
        # Called by boto3 with the number of bytes transferred so far
        with self._lock:
            self._seen_so_far += bytes_amount
            percent = (self._seen_so_far / self._size) * 100 if self._size else 0
            self._update_fn(self._filename, self._seen_so_far, self._size, percent)


class S3UploaderApp:
    def __init__(self, root):
        self.root = root
        root.title('S3 协议对象存储上传工具')
        root.geometry('880x640')

        # Top: Configuration
        cfg_frame = Frame(root, pady=6)
        cfg_frame.pack(fill='x')

        Label(cfg_frame, text='Endpoint URL:').grid(row=0, column=0, sticky='w')
        self.endpoint_var = StringVar(value='https://s3.example.com')
        Entry(cfg_frame, textvariable=self.endpoint_var, width=36).grid(row=0, column=1, padx=4)

        Label(cfg_frame, text='Bucket:').grid(row=0, column=2, sticky='w')
        self.bucket_var = StringVar(value='my-bucket')
        Entry(cfg_frame, textvariable=self.bucket_var, width=18).grid(row=0, column=3, padx=4)

        Label(cfg_frame, text='Base public URL (optional):').grid(row=1, column=0, sticky='w')
        self.baseurl_var = StringVar(value='https://cdn.example.com')
        Entry(cfg_frame, textvariable=self.baseurl_var, width=36).grid(row=1, column=1, padx=4)

        Label(cfg_frame, text='Prefix (path in bucket):').grid(row=1, column=2, sticky='w')
        self.prefix_var = StringVar(value='')
        Entry(cfg_frame, textvariable=self.prefix_var, width=18).grid(row=1, column=3, padx=4)

        Label(cfg_frame, text='Access Key:').grid(row=2, column=0, sticky='w')
        self.access_var = StringVar()
        Entry(cfg_frame, textvariable=self.access_var, width=36).grid(row=2, column=1, padx=4)

        Label(cfg_frame, text='Secret Key:').grid(row=2, column=2, sticky='w')
        self.secret_var = StringVar()
        Entry(cfg_frame, textvariable=self.secret_var, width=18, show='*').grid(row=2, column=3, padx=4)

        self.public_var = IntVar(value=1)
        Checkbutton(cfg_frame, text='Make uploaded objects public (ACL=public-read)', variable=self.public_var).grid(row=3, column=0, columnspan=2, sticky='w')

        # Middle: File selection and controls
        mid_frame = Frame(root)
        mid_frame.pack(fill='both', expand=True, padx=6, pady=6)

        left_frame = Frame(mid_frame)
        left_frame.pack(side=LEFT, fill='both', expand=True)

        Label(left_frame, text='Files to upload:').pack(anchor='w')

        list_frame = Frame(left_frame)
        list_frame.pack(fill='both', expand=True)

        self.file_listbox = Listbox(list_frame, selectmode=SINGLE)
        self.file_listbox.pack(side=LEFT, fill='both', expand=True)

        scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        btns_frame = Frame(left_frame, pady=6)
        btns_frame.pack(fill='x')
        Button(btns_frame, text='Add Files...', command=self.add_files).pack(side=LEFT, padx=4)
        Button(btns_frame, text='Remove Selected', command=self.remove_selected).pack(side=LEFT, padx=4)
        Button(btns_frame, text='Clear', command=self.clear_files).pack(side=LEFT, padx=4)

        right_frame = Frame(mid_frame)
        right_frame.pack(side=RIGHT, fill='y')

        Label(right_frame, text='Upload Controls:').pack(anchor='w')
        Button(right_frame, text='Test Connection', width=18, command=self.test_connection).pack(pady=4)
        Button(right_frame, text='Start Upload', width=18, command=self.start_upload).pack(pady=4)
        Button(right_frame, text='Stop All', width=18, command=self.stop_all).pack(pady=4)

        Label(right_frame, text='Max Threads:').pack(anchor='w', pady=(8, 0))
        self.max_threads_var = StringVar(value='3')
        Entry(right_frame, textvariable=self.max_threads_var, width=6).pack(anchor='w')

        # Progress and logs
        bottom_frame = Frame(root)
        bottom_frame.pack(fill='both', expand=False, padx=6, pady=6)

        Label(bottom_frame, text='Progress:').pack(anchor='w')
        self.progress_bar = ttk.Progressbar(bottom_frame, orient=HORIZONTAL, length=700)
        self.progress_bar.pack(fill='x')

        Label(bottom_frame, text='Log:').pack(anchor='w')
        self.log = ScrolledText(bottom_frame, height=10)
        self.log.pack(fill='both', expand=True)

        # Internal
        self._files = []  # list of file paths
        self._stop_flag = threading.Event()
        self._upload_threads = []
        self._task_queue = queue.Queue()

    def log_msg(self, msg: str):
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        self.log.insert(END, f'[{ts}] {msg}\n')
        self.log.see('end')

    def add_files(self):
        paths = filedialog.askopenfilenames(title='Select files to upload')
        for p in paths:
            p = str(Path(p).resolve())
            if p not in self._files:
                self._files.append(p)
                self.file_listbox.insert(END, p)
        self.log_msg(f'Added {len(paths)} file(s)')

    def remove_selected(self):
        sel = self.file_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        val = self.file_listbox.get(idx)
        self._files.remove(val)
        self.file_listbox.delete(idx)
        self.log_msg(f'Removed: {val}')

    def clear_files(self):
        self._files.clear()
        self.file_listbox.delete(0, END)
        self.log_msg('Cleared file list')

    def create_s3_client(self):
        endpoint = self.endpoint_var.get().strip()
        access = self.access_var.get().strip() or None
        secret = self.secret_var.get().strip() or None
        if not endpoint:
            raise ValueError('Endpoint URL is required')
        config = Config(signature_version='s3v4')
        session = boto3.session.Session()
        client = session.client('s3',
                                endpoint_url=endpoint,
                                aws_access_key_id=access,
                                aws_secret_access_key=secret,
                                config=config)
        return client

    def test_connection(self):
        try:
            client = self.create_s3_client()
            buckets = client.list_buckets()
            self.log_msg('Connection OK — found %d buckets' % len(buckets.get('Buckets', [])))
        except Exception as e:
            self.log_msg('Connection failed: %s' % str(e))

    def start_upload(self):
        if not self._files:
            self.log_msg('No files to upload')
            return
        try:
            max_threads = int(self.max_threads_var.get())
        except Exception:
            max_threads = 3
        self._stop_flag.clear()
        self.progress_bar['value'] = 0
        total_bytes = sum(os.path.getsize(p) for p in self._files)
        self._total_bytes = total_bytes
        self._uploaded_bytes = 0

        # Enqueue tasks
        for p in self._files:
            self._task_queue.put(p)

        for i in range(max_threads):
            t = threading.Thread(target=self._worker_thread, daemon=True)
            t.start()
            self._upload_threads.append(t)
        self.log_msg(f'Started upload with {max_threads} threads')

        # Monitor thread to update overall progress bar
        threading.Thread(target=self._monitor_progress, daemon=True).start()

    def stop_all(self):
        self._stop_flag.set()
        # clear queue
        while not self._task_queue.empty():
            try:
                self._task_queue.get_nowait()
            except Exception:
                break
        self.log_msg('Stop signal sent')

    def _worker_thread(self):
        client = None
        try:
            client = self.create_s3_client()
        except Exception as e:
            self.log_msg(f'Error creating S3 client: {e}')
            return

        transfer_config = TransferConfig(multipart_threshold=5 * 1024 * 1024, max_concurrency=4,
                                         multipart_chunksize=5 * 1024 * 1024, use_threads=True)

        while not self._stop_flag.is_set():
            try:
                path = self._task_queue.get(timeout=1)
            except Exception:
                break
            try:
                self._upload_file(client, path, transfer_config)
            except Exception as e:
                self.log_msg(f'Upload error for {path}: {e}')
            finally:
                self._task_queue.task_done()

    def _upload_file(self, client, path, transfer_config):
        bucket = self.bucket_var.get().strip()
        prefix = self.prefix_var.get().strip().lstrip('/')
        if not bucket:
            raise ValueError('Bucket name required')

        key = os.path.basename(path)
        if prefix:
            key = f"{prefix.rstrip('/')}/{key}"

        extra_args = {}
        if self.public_var.get():
            extra_args['ACL'] = 'public-read'

        content_type, _ = mimetypes.guess_type(path)
        if content_type:
            extra_args['ContentType'] = content_type

        filesize = os.path.getsize(path)

        def per_file_update(filename, seen, size, percent):
            # update overall uploaded bytes and progress bar incrementally
            # We compute delta and add to global uploaded bytes
            # For simplicity, we update progress bar to (uploaded_bytes + seen_of_current) / total
            try:
                # Not thread-safe perfect accuracy — fine for UI approximate progress
                self._last_seen = getattr(self, '_last_seen', {})
                last = self._last_seen.get(filename, 0)
                delta = seen - last
                self._last_seen[filename] = seen
                self._uploaded_bytes += delta
                overall_pct = (self._uploaded_bytes / self._total_bytes) * 100 if self._total_bytes else 0
                self.progress_bar['value'] = overall_pct
            except Exception:
                pass

        cb = ProgressPercentage(path, filesize, per_file_update)

        self.log_msg(f'Uploading {path} -> s3://{bucket}/{key} ({filesize} bytes)')
        client.upload_file(Filename=path, Bucket=bucket, Key=key, ExtraArgs=extra_args,
                           Config=transfer_config, Callback=cb)

        # on success
        public_url = self._make_public_url(key)
        self.log_msg(f'Uploaded: {path} -> {public_url or f"s3://{bucket}/{key}"}')
        # copy to clipboard for convenience
        try:
            if public_url:
                if HAVE_PYPERCLIP:
                    pyperclip.copy(public_url)
                    self.log_msg('Public URL copied to clipboard (pyperclip)')
                else:
                    # fallback to Tk clipboard
                    self.root.clipboard_clear()
                    self.root.clipboard_append(public_url)
                    self.log_msg('Public URL copied to clipboard (tk)')
        except Exception:
            pass

    def _make_public_url(self, key: str):
        base = self.baseurl_var.get().strip()
        if base:
            # join and ensure no duplicate slashes
            return f"{base.rstrip('/')}/{key.lstrip('/')}"
        # If no base provided, attempt to build from endpoint + bucket + key
        endpoint = self.endpoint_var.get().strip().rstrip('/')
        bucket = self.bucket_var.get().strip()
        if endpoint and bucket:
            # common pattern: https://{endpoint}/{bucket}/{key} OR https://{bucket}.{endpoint}/{key}
            # We choose path style to be safer
            return f"{endpoint}/{bucket}/{key}"
        return None

    def _monitor_progress(self):
        while not self._stop_flag.is_set() and (not self._task_queue.empty() or any(t.is_alive() for t in self._upload_threads)):
            try:
                self.progress_bar.update()
            except Exception:
                pass
            time.sleep(0.2)
        self.progress_bar['value'] = 100
        self.log_msg('All tasks finished or stopped')


if __name__ == '__main__':
    root = Tk()
    app = S3UploaderApp(root)
    root.mainloop()
