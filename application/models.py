from application import db


class Feeds(db.Model):
    __tablename__ = 'feeds'
    ID = db.Column(db.Integer, primary_key=True)
    SC_Group_ID = db.Column(db.Integer, unique=False)
    SC_Group_Desc = db.Column(db.String(80), unique=False)
    SC_GroupCommod_ID = db.Column(db.Integer, unique=False)
    SC_GroupCommod_Desc = db.Column(db.String(120), unique=False)
    SC_Geography_ID = db.Column(db.Integer, unique=False)
    Timeperiod_ID = db.Column(db.Integer, unique=False)
    Timeperiod_Desc = db.Column(db.String(120), unique=False)
    Amount = db.Column(db.Integer, unique=False)

    def __init__(self, notes):
        self.SC_Group_ID = notes

    def __repr__(self):
        return '<ID %r>' % self.ID


class RainFeeds(db.Model):
    __tablename__ = 'rainfeeds'
    ID = db.Column(db.Integer, primary_key=True)
    A = db.Column(db.String(300), unique=False)
    B = db.Column(db.String(100), unique=False)
    L = db.Column(db.Float, unique=False)
    M = db.Column(db.Float, unique=False)
    P = db.Column(db.Float, unique=False)

    def __init__(self, _id, a, b, l, m, p):
        self.ID = _id
        self.A = a
        self.B = b
        self.L = l
        self.M = m
        self.P = p

    def __repr__(self):
        return '<ID %r,A %r,B %r,L %r,M %r,P %r>' %(self.ID, self.A, self.B, self.L, self.M, self.P)