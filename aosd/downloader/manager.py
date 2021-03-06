from __future__ import absolute_import

from ..logging_helper import logging_helper

try:
    import urllib.request as comp_urlreq # For Python 3.0 and later
    import urllib.error as compat_urlerr
    import http.client as compat_http
    import urllib.parse as comp_urlparse
except ImportError:
    import urllib2 as comp_urlreq # Fall back to Python 2's urllib2
    import urllib2 as comp_urlerr
    import httplib as compat_http
    import urlparse as comp_urlparse
import os
import gzip
import tarfile

from .config import config
from .Builds import Builds

class manager(object):

    @classmethod
    def CreateTarballURL(cls, release_type, package_name, build_number):
        default_scheme = 'https'
        if config.getUseHTTPS() == False:
            default_scheme = 'http'
        default_url = default_scheme+'://opensource.apple.com/tarballs/'+package_name+'/'+package_name+'-'+build_number+'.tar.gz'
        parsed_url = comp_urlparse.urlparse(default_url)
        return parsed_url.geturl()

    @classmethod
    def CreatePlistURL(cls, plist_name):
        default_scheme = 'https'
        if config.getUseHTTPS() == False:
            default_scheme = 'http'
        default_url = default_scheme+'://opensource.apple.com/plist/'+plist_name
        parsed_url = comp_urlparse.urlparse(default_url)
        return parsed_url.geturl()

    @classmethod
    def DownloadFileFromURLToPath(cls, url_address, file_path):
        request = comp_urlreq.Request(url_address)
        if config.getVerboseLogging() == True:
            logging_helper.getLogger().info('Starting download from  "'+url_address+'" -> "'+file_path+'"...')
        response = None
        try:
            response = comp_urlreq.urlopen(request)
        except comp_urlerr.HTTPError as e:
            logging_helper.getLogger().error('HTTPError = '+str(e.code)+' on '+url_address)
            response = None
        except comp_urlerr.URLError as e:
            logging_helper.getLogger().error('URLError = '+ str(e.reason)+' on '+url_address)
            response = None
        except compat_http.HTTPException as e:
            logging_helper.getLogger().error('HTTPException on '+url_address)
            response = None
        except Exception:
            logging_helper.getLogger().error(':Exception :( on '+url_address)
            response = None
        if response != None:
            output = open(file_path, 'wb')
            output.write(response.read())
            output.close()
            if config.getVerboseLogging() == True:
                logging_helper.getLogger().info('Download Complete!')

    @classmethod
    def DownloadPackageTarball(cls, release_type, package_name, build_number):
        downloaded_directory_path = ''
        tarball_address = cls.CreateTarballURL(release_type, package_name, build_number)
        package_file_name = os.path.basename(tarball_address)
        output_directory = os.path.expanduser(config.getDownloadDir())
        output_file = os.path.join(output_directory, package_file_name)
        try:
            cls.DownloadFileFromURLToPath(tarball_address, output_file)
            tar_name = os.path.splitext(package_file_name)[0]
            if config.getVerboseLogging() == True:
                logging_helper.getLogger().info('Decompressing "'+output_file+'" -> "'+tar_name+'"...')
            gz_archive = gzip.open(output_file, 'rb')
            if config.getVerboseLogging() == True:
                logging_helper.getLogger().info('Reading file contents...')
            file_content = gz_archive.read()
            tar_path = os.path.join(output_directory, tar_name)
            dump_tar = open(tar_path, 'wb')
            if config.getVerboseLogging() == True:
                logging_helper.getLogger().info('Dumping tar file...')
            dump_tar.write(file_content)
            if config.getVerboseLogging() == True:
                logging_helper.getLogger().info('Closing files...')
            dump_tar.close()
            gz_archive.close()
            if config.getVerboseLogging() == True:
                logging_helper.getLogger().info('Removing archive...')
            os.remove(output_file)
            if config.getVerboseLogging() == True:
                logging_helper.getLogger().info('Opening tar file...')
            tar_archive = tarfile.open(tar_path)
            if config.getVerboseLogging() == True:
                logging_helper.getLogger().info('Decompressing tar file...')
            tar_archive.extractall(output_directory)
            if config.getVerboseLogging() == True:
                logging_helper.getLogger().info('Closing tar file...')
            tar_archive.close()
            if config.getVerboseLogging() == True:
                logging_helper.getLogger().info('Removing tar file...')
            os.remove(tar_path)
            if config.getVerboseLogging() == True:
                logging_helper.getLogger().info('Decompression Complete!')
            file_name = os.path.splitext(tar_name)[0]
            logging_helper.getLogger().info('The package "'+file_name+'" has been downloaded to "'+output_directory+'".')
            downloaded_directory_path = os.path.join(output_directory, file_name)
        except:
            logging_helper.getLogger().error('Could not find tarball!')
        return downloaded_directory_path

    @classmethod
    def DownloadPackageManifest(cls, cached_plist_file_path):
        plist_name = os.path.basename(cached_plist_file_path)
        plist_url = cls.CreatePlistURL(plist_name)
        if os.path.exists(cached_plist_file_path) == False:
            cls.DownloadFileFromURLToPath(plist_url, cached_plist_file_path)

    @classmethod
    def RemovePackageManifest(cls, cached_plist_file_path):
        file_name = os.path.basename(cached_plist_file_path)
        if file_name != 'paackage_cache.plist' and file_name != 'aosd.plist':
            if os.path.exists(cached_plist_file_path) == True:
                os.remove(cached_plist_file_path)

    @classmethod
    def ValidateAndDownload(cls, release_type, package_name, build_number):
        downloaded_directory_path = None
        has_valid_build = build_number in Builds.get(release_type, package_name)
        if has_valid_build == True:
            downloaded_directory_path = cls.DownloadPackageTarball(release_type, package_name, build_number)
        else:
            logging_helper.getLogger().error('Invalid build number! Please use the "--list" flag to see available build numbers for a package.')
        return downloaded_directory_path
