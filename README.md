# sftpmgr
## SFTP Stack Manager CLI Tool for OpsWorks cookbook

This script adds users and private keys to SFTP stacks as created by a cookbook like [this one](https://github.com/ethanmcc/opsworks-cookbooks/tree/release-chef-11.10/sftp). The script asks you to choose an AWS OpsWorks stack that implements the SFTP cookbook. Then it allows you to create users (a password will be generated), or add public keys to existing users. Once you're through making changes, the script lists the changes made and asks if you'd like to update the stack now:

	Make more changes? [y/N]
	
	Pending updates for stack My Test Stack
	--------------------------------------------------------
	1. Created user jolnston - aizh7uorIeTv
	2. Added public key for jolnston - ssh-rsa ASKdjhaskdjhaskjdhaskjdhAKJSDH jolnston@jolnstonmail.com
	3. Created user schwantzin - xnek5tOiywMd
	
	Update stack now? [Y/n]

If you select yes, the script updates your stack JSON and runs Setup on the stack.

### Credentials

This app connects to AWS via boto. That means it can gather your credentials from the `~/.aws/credentials` file. The default profile is assumed unless you set `AWS_PROFILE` to a different profile name in your environment.