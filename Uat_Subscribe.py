import psycopg2,time
import yaml,os
# from Config import ConfigSql,ConfigDatabase


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

class config:
    configDatabase = ConfigDatabase()
    configSql = ConfigSql()

class uatSubscribe(config):
    '''封装方法'''
    
    #连接数据库，执行sql，关闭连接
    def dataCenterExecute(self,center,sql):
        #获取数据库信息
        self.database_Data = self.configDatabase.operateYaml('UAT')
        db = None
        #连接数据库
        try:
            db = psycopg2.connect(database=center,user=self.database_Data['username'], password=self.database_Data['password'], host=self.database_Data['host'], port=self.database_Data['port'])
            db.autocommit = True
            cur = db.cursor()
            print(sql)
            cur.execute(sql)
            self.result = cur.fetchall()
            cur.close()
            if self.result is not None:
                print(self.result)
                return self.result
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)
        finally:
            if db is not None:
                db.close()
    
    #清空数据中心所有的表
    def clearTable(self):
        # select tablename from pg_tables where tablename like 'lc%' or tablename like 'tc%' or tablename like  'stc%' or tablename like  'ctc%';   查询出所有的表
        # TRUNCATE tablename RESTART IDENTITY;    清空表数据并还原 sequence
        self.result = self.dataCenterExecute('datacenter',"select tablename from pg_tables where tablename like 'lc%' or tablename like 'tc%' or tablename like  'stc%' or tablename like  'ctc%';")
        try:
            print('\n--------------开始删除表数据----------')
            for name in range(0,len(self.result)):
                self.tablename = str(self.result[name]).replace('\'','').replace(',','').replace('(','').replace(')','')
                self.sql = "TRUNCATE {} RESTART IDENTITY;".format(self.tablename)
                self.dataCenterExecute('datacenter',self.sql)
                print('清除 %s 表数据!' % self.tablename)
            print('--------------删除表数据结束----------\n')
        except Exception as e:
            print(e)

    # 根据步骤连接数据库并执行
    def part(self,part):
        try:
            self.data = config.configSql.operateYaml(part)
            for num in range(0,len(self.data)):
                self.center = self.data[num]['center']
                self.sql = self.data[num]['sql']
                for i in range(0,len(self.sql)):
                    time.sleep(1)
                    self.dataCenterExecute(self.center,self.sql[i])
        except Exception as e:
            print(e)
    


class main(uatSubscribe):
    '''执行逻辑'''
    uatSubscribe = uatSubscribe()
    # 第一步，删除数据中心所有的订阅,之后清空所有的表
    # 第一步，删除数据中心所有表的数据
    print('==================================================')
    print('=============测试环境重新订阅开始===================')
    print('==================================================')
    uatSubscribe.part('part1')
    uatSubscribe.clearTable()
    # 第二步，删除各个中心所有的插槽，并重建
    uatSubscribe.part('part2')
    # 第三步，重建数据中心所有的订阅
    uatSubscribe.part('part3')
    print('==================================================')
    print('=============测试环境重新订阅结束===================')
    print('==================================================')



if __name__ == "__main__":
    main()
