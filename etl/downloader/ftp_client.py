import ftplib
from etl.downloader.protocols import FTPClientInterface

class DefaultFTPClient(FTPClientInterface):
    """
    Default FTP client adapter (Adapter Pattern) that encapsulates ftplib.FTP.
    """
    def login_and_cwd(self, host: str, user: str, passwd: str, year: int) -> ftplib.FTP:
        ftp = ftplib.FTP(host, timeout=30)
        ftp.login(user, passwd)
        ftp.cwd(f"/pub/data/gsod/{year}")
        return ftp