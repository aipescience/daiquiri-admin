import os
import pwd
import spwd
import grp
import subprocess


class Machine():
    def __init__(self, dryrun=True, default_gid=2000, uid_range=[2000, 3000]):
        self.dryrun = dryrun
        self.default_gid = default_gid
        self.uid_range = uid_range

    def call(self, cmd):
        if self.dryrun:
            print cmd
        else:
            subprocess.call(cmd, shell=True)

    def mkdir(self, path):
        if self.dryrun:
            print 'os.mkdir(\'%s\')' % path
        else:
            os.mkdir(path)

    def chown(self, path, uid, gid):
        u = int(uid)
        g = int(gid)

        if self.dryrun:
            print 'os.chown(\'%s\', %i, %i)' % (path, u, g)
        else:
            os.chown(path, u, g)

    def get_new_uid(self):
        uid = self.uid_range[0]
        for system_user in sorted(pwd.getpwall(), key=lambda k: k.pw_uid):
            if system_user.pw_uid <= self.uid_range[1] and system_user.pw_uid > uid:
                uid = system_user.pw_uid
        return uid + 1

    def get_full_name(self, user):
        return user['details']['firstname'] + ' ' + user['details']['lastname']

    def create_user(self, user, password):
        # get the username
        username = user['username']

        # check if the user exists already
        try:
            pwd.getpwnam(username)
            raise Exception('User %s already exists.' % username)
        except KeyError:
            pass

        # get the uid for the new user
        try:
            uid = int(user['details']['UID'])
        except KeyError:
            uid = self.get_new_uid()

        # check if the uid is not already there
        try:
            pwd.getpwuid(uid)
            raise Exception('UID %s already exists.' % uid)
        except KeyError:
            pass

        # get the gid for the new user
        try:
            gid = int(user['details']['GID'])
        except KeyError:
            gid = self.default_gid

        # check if the gid exists
        try:
            grp.getgrgid(gid)
        except KeyError:
            raise Exception('GID %s does not exist.' % gid)

        # get the fullname
        fullname = self.get_full_name(user)

        # create new user on the machine
        print 'creating user', username
        self.call("useradd -m -s /bin/bash -u %i -g %i -p '%s' -c '%s' %s" % (uid, gid, password, fullname, username))

        return uid, gid

    def update_user(self, user, password):
        # get the username
        username = user['username']

        # check if the user exists, if not return silently
        try:
            system_user = pwd.getpwnam(username)
            system_password = spwd.getspnam(username)
        except KeyError:
            return

        # enable the user if he or she was disabled
        if (system_password.sp_pwd.startswith('!')):
            print 'unlocking user', username
            self.call("usermod -U %s" % username)

            # fetch proper password
            system_password = spwd.getspnam(username)

        # a flag if uid or gid have changed
        uid_gid_changed = False

        # check full name
        fullname = self.get_full_name(user)

        if (fullname != system_user.pw_gecos.decode('utf-8')):
            print 'updating fullname (i.e. comment) for', username
            self.call(u'usermod -c \'%s\' %s' % (fullname, username))

        # check uid
        if (int(user['details']['UID']) != system_user.pw_uid):
            print 'updating uid for', username
            self.call("usermod -u '%s' %s" % (user['details']['UID'], username))
            uid_gid_changed = True

        # check gid
        if (int(user['details']['GID']) != system_user.pw_gid):
            print 'updating gid for', username
            self.call("usermod -g '%s' %s" % (user['details']['GID'], username))
            uid_gid_changed = True

        # check password
        if (password != system_password.sp_pwd):
            print 'updating password for', username
            self.call("usermod -p '%s' %s" % (password, username))

        return uid_gid_changed

    def disable_user(self, username):
        # check if the user exists, if not return silently
        try:
            system_password = spwd.getspnam(username)
        except KeyError:
            return

        # check if the user is alredy locked, if yes return silently
        if (system_password.sp_pwd.startswith('!')):
            return

        # lock the user
        print 'locking user', username
        self.call("usermod -L %s" % username)
