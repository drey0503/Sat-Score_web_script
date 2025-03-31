import paramiko
import os


def delete_files_in_folder(folder_path):
    """Deletes all files in the specified folder."""

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

# connect to SFTP directory using paramiko client
class MySFTPClient(paramiko.SFTPClient):

    def put_dir(self, source, target):
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item),
                             '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        try:
            super(MySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise
# login into SFTP

transport = paramiko.Transport("***REDACTED***", 22)
transport.connect(username="*REDACTED",
                  password="*REDACTED*")
sftp = MySFTPClient.from_transport(transport)
# should lead to sftp directory path
sftp.mkdir("/incoming/**REDACTED**", ignore_existing=True)
sftp.put_dir(r"C:\Users\dreyson\Desktop\SAT_Files",
             "/incoming/**REDACTED**")

folder_path = r"C:\Users\dreyson\Desktop\SAT_Files"
delete_files_in_folder(folder_path)
print("Script Complete! Files sent off to SFTP!")
