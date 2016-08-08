
def get_mesh_status(zdcli):
    res=zdcli.do_cmd('show mesh info')
    return res.split('Mesh Status=')[1].split('\r\r\n')[0].strip()