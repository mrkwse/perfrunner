import os.path
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
from operator import add

from perfrunner.logger import logger


def safe(method):
    def wrapper(*args, **kargs):
        try:
            return method(*args, **kargs)
        except (NoSectionError, NoOptionError), e:
            logger.interrupt('Failed to get option from config: {0}'.format(e))
    return wrapper


class Config(object):

    def parse(self, fname):
        logger.info('Reading configuration file: {0}'.format(fname))
        if not os.path.isfile(fname):
            logger.interrupt('File doesn\'t exist: {0}'.format(fname))
        self.config = ConfigParser()
        self.config.read(fname)


class ClusterSpec(Config):

    @safe
    def get_clusters(self):
        return tuple(
            servers.split() for _, servers in self.config.items('clusters')
        )

    @safe
    def get_hosts(self):
        split_host_port = lambda server: server.split(':')[0]
        return map(split_host_port, reduce(add, self.get_clusters()))

    @safe
    def get_paths(self):
        data_path = self.config.get('storage', 'data')
        index_path = self.config.get('storage', 'index')
        return data_path, index_path

    @safe
    def get_rest_credentials(self):
        return self.config.get('credentials', 'rest').split(':')

    @safe
    def get_ssh_credentials(self):
        return self.config.get('credentials', 'ssh').split(':')


class TestConfig(Config):

    @safe
    def get_mem_quota(self):
        return self.config.getint('cluster', 'mem_quota')

    @safe
    def get_initial_nodes(self):
        return self.config.getint('cluster', 'initial_nodes')

    @safe
    def get_num_buckets(self):
        return self.config.getint('cluster', 'buckets')

    @safe
    def get_compaction_options(self):
        if 'compaction' in self.config.sections():
            return dict((p, v) for p, v in self.config.items('compaction'))