from doula.models.sites import Package

if __name__ == "__main__":
    p = Package("dummycode", "1.3.1")
    p.distribute("master", "1.3.2")
