import psycopg2,time
import yaml,os
# from Config import ConfigSql,ConfigDatabase

sql_filename = str(os.getcwd()) + '\\' + 'Uat_Sql.yaml'
data_filename =  str(os.getcwd()) + '\\' + 'Database.yaml'

class config:
    # configDatabase = ConfigDatabase()
    # configSql = ConfigSql()
    def operateYaml(self,filename,value):
        if os.path.exists(filename):
            #读取YAML文件的数据
            with open(filename, encoding='utf-8') as f: 
                self.data = yaml.safe_load(f.read())
            return self.data[value]
        else:
            print('文件不存在！')

class uatSubscribe(config):
    '''封装方法'''
    config = config()
    #连接数据库，执行sql，关闭连接
    def dataCenterExecute(self,center,sql):
        #获取数据库信息
        self.database_Data = self.config.operateYaml(data_filename,'UAT')
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
            self.data = self.config.operateYaml(sql_filename,part)
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
    # 第一步，删除数据中心所有的订阅
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
