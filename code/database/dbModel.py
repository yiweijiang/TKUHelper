from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hvalxhbivmvemz:fc9d48eaccdd02ef1587366ce1315a92a8739daf88b7b38fa9cef148041f85c4@ec2-23-23-110-26.compute-1.amazonaws.com:5432/df1pnl2mdjpdds'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


class Notebook(db.Model):
    __tablename__ = 'Notebook'
    id = db.Column(db.Integer, primary_key=True)
    USER_ID = db.Column(db.String(64))
    Event = db.Column(db.String(64))
    Time = db.Column(db.String(64))
    Description = db.Column(db.String(128))
    RemindTime = db.Column(db.DateTime())
    WhenRemind = db.Column(db.String(16))

def __init__(self,USER_ID,Event,Time,Description,RemindTime,WhenRemind):
    self.USER_ID = USER_ID
    self.Event = Event
    self.Time = Time
    self.Description = Description
    self.RemindTime = RemindTime
    self.WhenRemind = WhenRemind

class USER_DATA(db.Model):
    __tablename__ = 'USER_DATA'
    id = db.Column(db.Integer, primary_key=True)
    LINE_ID = db.Column(db.String(64))
    Add_Event = db.Column(db.String(64))
    Add_Time = db.Column(db.String(64))
    Add_Index = db.Column(db.Integer)
    Change_Event = db.Column(db.String(64))
    Change_Type = db.Column(db.String(64))
    Change_Index = db.Column(db.Integer)
    Delete_Event = db.Column(db.String(64))
    Curriculum_Cookie = db.Column(db.String(128))
    Status = db.Column(db.Integer)
    Student_ID = db.Column(db.Integer)
    #PWD = db.Column(db.String(512))
    #PWD = db.Column(db.LargeBinary())
    Remind = db.Column(db.Boolean)
    encrypt = db.Column(db.LargeBinary())
    LastCource = db.Column(db.String(256))

def __init__(self,LINE_ID,Add_Event,Add_Time,Add_Index,Change_Event,Change_Type,Change_Index, Delete_Event,Curriculum_Cookie,Status,Student_ID,Remind,encrypt,LastCource):
    self.LINE_ID = LINE_ID
    self.Add_Event = Add_Event
    self.Add_Time = Add_Time
    self.Add_Index = Add_Index
    self.Change_Event = Change_Event
    self.Change_Type = Change_Type
    self.Change_Index = Change_Index
    self.Delete_Event = Delete_Event
    self.Curriculum_Cookie = Curriculum_Cookie
    self.Status = Status
    self.Student_ID = Student_ID
    self.Remind = Remind
    self.encrypt = encrypt
    self.LastCource = LastCource

class Apple_Realtime_News(db.Model):
    __tablename__ = 'Apple_Realtime_News'
    id = db.Column(db.Integer, primary_key=True)
    TITLE = db.Column(db.String(64))
    DATE = db.Column(db.String(64))
    URL = db.Column(db.String(128))
    IMAGE_URL = db.Column(db.String(128))
    NEWS_Type = db.Column(db.String(8))

def __init__(self,TITLE,DATE,URL,IMAGE_URL,NEWS_Type):
    self.TITLE = TITLE
    self.DATE = DATE
    self.URL = URL
    self.IMAGE_URL = IMAGE_URL
    self.NEWS_Type = NEWS_Type

class Tech_News(db.Model):
    __tablename__ = 'Tech_News'
    id = db.Column(db.Integer, primary_key=True)
    TITLE = db.Column(db.String(128))
    URL = db.Column(db.String(256))
    IMAGE_URL = db.Column(db.String(256))

def __init__(self,TITLE,URL,IMAGE_URL):
    self.TITLE = TITLE
    self.URL = URL
    self.IMAGE_URL = IMAGE_URL

class Elective_Data(db.Model):
    __tablename__ = 'Elective_Data'
    id = db.Column(db.Integer, primary_key=True)
    Student_ID = db.Column(db.Integer)
    Cource = db.Column(db.Integer)
    Number = db.Column(db.Integer)

def __init__(self,Student_ID,Cource,Number):
    self.Student_ID = Student_ID
    self.Cource = Cource
    self.Number = Number

class Cource(db.Model):
    __tablename__ = 'Cource'
    id = db.Column(db.Integer, primary_key=True)
    Number = db.Column(db.Integer)
    Teacher = db.Column(db.String(64))
    Name = db.Column(db.String(128))
    Time = db.Column(db.Text)
    Week = db.Column(db.String(16))
    SourceTime = db.Column(db.Integer)

def __init__(self,Number,Teacher,Name,Time,Week,SourceTime):
    self.Number = Number
    self.Teacher = Teacher
    self.Name = Name
    self.Time = Time
    self.Week = Week
    self.SourceTime = SourceTime

class Weather_Data(db.Model):
    __tablename__ = 'Weather_Data'
    id = db.Column(db.Integer, primary_key=True)
    Humidity = db.Column(db.String(8))
    Temprature = db.Column(db.String(8))
    Feel_Temprature = db.Column(db.String(8))
    Railfall_Random = db.Column(db.String(8))
    Weather_Status = db.Column(db.String(16))
    Time = db.Column(db.String(16))
def __init__(self,Humidity,Temprature,Feel_Temprature,Railfall_Random,Weather_Status,Time):
    self.Humidity = Humidity
    self.Temprature = Temprature
    self.Feel_Temprature = Feel_Temprature
    self.Railfall_Random = Railfall_Random
    self.Weather_Status = Weather_Status
    self.Time = Time



class Calendar(db.Model):
    __tablename__ = 'Calendar'
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(16))
    Year = db.Column(db.Integer)
    Month = db.Column(db.String(8))
    Day = db.Column(db.String(8))
    
def __init__(self,Name,Year,Month,Day):
    self.Name = Name
    self.Year = Year
    self.Month = Month
    self.Day = Day


if __name__ == '__main__':
    manager.run()
