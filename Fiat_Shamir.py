import random
def setup():
    p= 61
    q=53
    n=p*q

    s= int(input("Enter secret number: "))
    v=pow(s,2,n)

    print(f"n= {n}")
    print(f"your secret s={s}")
    print(f"server stores v={v}")
    return n,s,v

def round_one(n,s,v):
    #step 1
    r= random.randint(2,n-1)
    x= pow(r,2,n)
    #step 2
    e=random.randint(0,1)
    #step 3
    if e==0:
        y=r
    else:
        y=(r*s)%n
    #step 4
    lhs= pow(y,2,n)
    rhs=(x* pow(v,e,n))%n

    return lhs==rhs

def run_impersonator():
    print("=== impersonator===")
    n,s,v= setup()
    fake_s= int(input(" Impersonator guesses secret: "))
    print()

    passed =0
    for i in range(20):
        result = round_one(n, fake_s,v)
        status= "PASS" if result else "FAIL"
        print(f"Round {i+1}: {status}")
        if result:
            passed+=1
    print(f"\n{passed}/20 rounds passed")
    if passed==20:
        print("Impersonator successful")
    else:
        print("Impersonator failed. Acesss Denied")
    

def run_legit():
    print("=== Legit Prover ===")
    n,s,v = setup()
    print()

    passed=0
    for i in range(20):
        result = round_one(n,s,v)
        status="PASS" if result else "FAIL"
        print(f"Round {i+1}: {status}")
        if result:
            passed+=1

    print(f"\n{passed}/20 rounds passed")
    if passed==20:
            print("Verififier approved. Login Successful!")
    else:
            print("Authorization failed")
run_legit()            
run_impersonator()















































