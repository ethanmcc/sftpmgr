import subprocess
import json
import random
import sys

import boto

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


class SFTPUserTool(object):
    @staticmethod
    def generate_password(pw_length=12):
        mypw = ''

        for i in range(pw_length):
            next_index = random.randrange(len(ALPHABET))
            mypw = mypw + ALPHABET[next_index]

        # replace 1 or 2 characters with a number
        for i in range(random.randrange(1, 3)):
            replace_index = random.randrange(len(mypw) // 2)
            mypw = '{}{}{}'.format(mypw[0:replace_index],
                                   str(random.randrange(10)),
                                   mypw[replace_index + 1:])

        # replace 1 or 2 letters with an uppercase letter
        for i in range(random.randrange(1, 3)):
            replace_index = random.randrange(len(mypw) // 2, len(mypw))
            mypw = '{}{}{}'.format(mypw[0:replace_index],
                                   mypw[replace_index].upper(),
                                   mypw[replace_index + 1:])

        return mypw

    def list_stacks(self):
        print('\nOpsWorks Stacks')

        for index, stack in enumerate(self.stacks):
            print('{}) {}'.format(index + 1, stack['Name']))

    def select_stack(self):
        stack_index = input('\nSelect a stack to modify: ')

        try:
            stack = self.stacks[int(stack_index) - 1]
        except (KeyError, ValueError):
            print('Invalid stack. Exiting...')
            sys.exit(1)
        return stack

    def update_user(self):
        username = input('What account would you like to modify? ')
        for user in self.users:
            if user['username'] == username:
                self.add_user_public_key(user)
                self.changes.append('Added public key for {} - {}'.format(
                    username, user['public_keys'][-1]))
                break
        else:
            print('\nUser not found. Aborting...')

    def create_user(self):
        username = input('Enter new username: ')
        if [u for u in self.users if u['username'] == username]:
            print('\nUser already exists. Aborting...')
            return

        passwd = self.generate_password()
        hashed_passwd = subprocess.getoutput(
            'openssl passwd -1 {}'.format(passwd))
        if '\n' in hashed_passwd:
            print('Unable to hash password: {}'.format(hashed_passwd))
            sys.exit(1)

        self.users.append({
            'username': username,
            'password': hashed_passwd,
        })
        self.changes.append(
            'Created user {} - {}'.format(username, passwd))
        print('Created user {}'.format(username))

    def list_users(self):
        print()
        for user in self.users:
            print(user['username'])

    def make_change(self):
        while True:
            action = input(
                '\n[C]reate user, [U]pdate user or [L]ist users? ').lower()
            if action in ('create', 'update', 'c', 'u'):
                break
            elif action in ('list', 'l'):
                self.list_users()

        if action.startswith('c'):
            self.create_user()
        elif action.startswith('u'):
            self.update_user()
        elif action.startswith('l'):
            self.list_users()

    def add_user_public_key(self, user):
        if input('\nAdd public key? [Y/n] ').lower() in ('', 'y'):
            keys = user.get('public_keys', [])
            key = input('\nEnter public key: ')
            if not key:
                print('Empty public key. Aborting...')
                return user
            keys.append(key)
            user['public_keys'] = keys

    def print_stack_changes(self):
        print(
            '\nPending updates for stack {}\n{}'.format(
                self.stack['Name'], (len(self.stack['Name']) + 26) * '-'))
        for index, change in enumerate(self.changes):
            print('{}. {}'.format(index + 1, change))

    def __init__(self):
        self.opsworks = boto.connect_opsworks()
        self.changes = []

    def run(self):
        self.stacks = self.opsworks.describe_stacks()['Stacks']
        self.list_stacks()
        self.stack = self.select_stack()

        custom_json = json.loads(self.stack.get('CustomJson', '{}'))
        sftp = custom_json.get('sftp', {})
        self.users = sftp.get('users', [])

        self.make_change()
        while input(
                'Make more changes? [y/N] ').lower() == 'y':
            self.make_change()
        sftp['users'] = self.users
        custom_json['sftp'] = sftp

        self.print_stack_changes()
        if input('\nUpdate stack now? [Y/n] ').lower() in ('', 'y'):
            self.opsworks.update_stack(
                self.stack['StackId'],
                custom_json=json.dumps(custom_json, indent=4, sort_keys=True))
            self.opsworks.create_deployment(self.stack['StackId'],
                                            command={'Name': 'setup'})


def execute():
    tool = SFTPUserTool()
    tool.run()


if __name__ == '__main__':
    execute()
