import yaml
import os

class ConfigSql:
    '''读取配置sql文件'''
    filename = str(os.getcwd()) + '\\' + 'Uat_Sql.yaml'
    if os.path.exists(filename):
        #返回指定步骤的数据
        def operateYaml(self,part):
            with open(self.filename, encoding='utf-8') as f: 
                self.data = yaml.safe_load(f.read())
            return self.data[part]
    else:
        print('config文件不存在！')

class ConfigDatabase:
    filename =  str(os.getcwd()) + '\\' + 'Database.yaml'
    if os.path.exists(filename):
        #返回指定的数据库配置
        def operateYaml(self,environment):
            with open(self.filename, encoding='utf-8') as f: 
                self.data = yaml.safe_load(f.read())
            return self.data[environment]
    else:
        print('config文件不存在！')


if __name__ == "__main__":
    data = ConfigSql().operateYaml('part2')
    data2 = ConfigDatabase().operateYaml('UAT')
    print(data2)