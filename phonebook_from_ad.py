#!/usr/bin/env python3

#
# create file config.yaml with similar parameters
#
# 'dc': 'dc.local'
# 'd_admin': 'admin'
# 'd_pass': 'password'
# 'phonebook': './phonebook.csv'
# 'base': 'dc=mydomain,dc=local'
# 'template_ext': 'extension,name,description,tech,secret,,,,,,,,,,,,,,,,,,,,recording_in_external,recording_out_external,recording_out_internal,recording_ondemand,enabled,recording_priority,sendrpid'
# 'template_users': 'username,password,default_extension,description,fname,lname,displayname'
#

from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
import ruamel.yaml as yaml


with open('config.yaml') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

dc = config['dc']
d_admin = config['d_admin']
d_pass = config['d_pass']
base = config['base']
phonebook = config['phonebook']
users = config['users']
template_ext = config['template_ext']
template_users = config['template_users']

server = Server(dc, get_info=ALL)
conn = Connection(server, user=d_admin, password=d_pass, auto_bind=True)
if conn.bind():
    search_filter_user = f'''(&
                              (|
                                (objectClass=Person)
                                (sAMAccountName=*)
                                (objectCategory=cn=Person,cn=Schema,
                                 cn=Configuration,{base})
                               )
                            )'''
    conn.search(search_base=base,
                search_filter=search_filter_user,
                attributes=['cn', 'ipPhone'])
    with open(phonebook, 'w', encoding='utf-8', newline='') as p, \
            open(users, 'w', encoding='utf-8', newline='') as u:
        p.write(template_ext)
        u.write(template_users)
        for entry in conn.entries:
            if entry.ipPhone:
                user_cn = entry.cn
                user_phone = entry.ipPhone
                p_line = f'{user_phone},{user_cn},{user_cn},pjsip,pbx{user_phone},,,,,,,,,,,,,,,,,,,,force,force,force,force,enabled,10,yes\n'
                u_line = f'{user_phone},pbx{user_phone},{user_phone},{user_phone},,{user_cn}\n'
                print(p_line)
                print(u_line)
                u.write(u_line)
                p.write(p_line)
    p.close()
    u.close()
