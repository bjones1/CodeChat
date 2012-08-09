from get_mods import get_mods, get_data_files
package_name = 'sphinx'
hiddenimports = get_mods(package_name)
print(hiddenimports)
datas = get_data_files(package_name)
