

def f(x,y):
    return x+y

print "3+4 was ", f(3,4)

def patch(fold):
    
    print fold

    def decorator(fneu):

        print fneu
        
        def wrapper(*a):
            print "wrapper called ", fold, a
            return fneu(fold, *a)

        fold = fneu        

    return decorator   
        

@patch(f)
def f_new(f_old, x,y):
    f_old(x,y+1)

print f_new

print "3+4 is  ", f(3,4)

    
