import uuid,time,random
def uniqid():
    return str(uuid.uuid5(uuid.uuid4(),str(time.time())))

if __name__ == '__main__':
    print uniqid()
