import paramiko
import tempfile
import shelve
import StringIO

class SSHExecutor():
    def __init__(self, ip_address, username="ubuntu", password="", key=None):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.key = key

    def _get_client(self):
        private_key = StringIO.StringIO(self.key)
        pkey=paramiko.RSAKey.from_private_key(private_key)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.ip_address, username=self.username, pkey=pkey)
        return client

    def execute_command(self, command):

        client = self._get_client()
        stdin, stdout, stderr = client.exec_command(command)
        output = "stdout:"
        for line in stdout:
            output += ' ' + line.strip('\n') + " " 
        output += " stderror:"
        for line in stderr:
            output += ' ' + line.strip('\n') + " "
        client.close()
        return output

    def download_file_from_container(self, path):
        f = tempfile.NamedTemporaryFile()

        client = self._get_client()
        sftp = client.open_sftp()
        sftp.getfo(path, f)
        sftp.close()
        client.close()
        f.seek(0)

        output = f.read()
        f.close()

        return output

    def upload_file(self, path, bytes):
        f = tempfile.NamedTemporaryFile()
        f.write(bytes)
        f.seek(0)

        client = self._get_client()
        sftp = client.open_sftp()
        sftp.putfo(f, remotepath=path)
        sftp.close()
        client.close()
        f.close()

    def upload_file_from_path(self, hostPath, remotePath):
        client = self._get_client()
        sftp = client.open_sftp()
        sftp.put(hostPath, remotePath)
        sftp.close()
        client.close()

    def _get_key_from_db(self):
        db = shelve.open('auths.db')

        key = None
        keypath = None

        if db.has_key(str(self.ip_address) + "_key"):
            key = db[str(self.ip_address) + "_key"]
        if db.has_key(str(self.ip_address) + "_keypath"):
            keypath = db[str(self.ip_address) + "_keypath"]
        db.close()

        return key, keypath
