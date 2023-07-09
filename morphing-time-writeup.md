# **UIUCTF2023: Morphing Time (crypto)**

So I was the member of my team who took a stab at most of the crypto challenges. Let me guide you through my thought process as I tried to solve this one!

# Understanding the given code
Although it is usually not the best idea, I'm going to go through the code from top to bottom, chunk by chunk.

## The Beginning
```python
#!/usr/bin/env python3
from Crypto.Util.number import getPrime
from random import randint

with open("/flag", "rb") as f:
    flag = int.from_bytes(f.read().strip(), "big")
```
Nothing really goes one here. This code just imports the necessary files and tells you that the flag **was** in bytes and has now been converted to an integer (not really important info, but it's cool to keep note of).

## The Setup
```python
def setup():
    # Get group prime + generator
    p = getPrime(512)
    g = 2

    return g, p
```
This function does exactly what it says: gets a prime and a generator. What exactly is a generator you may ask? A quick wikipedia search will lead you to [this](https://en.wikipedia.org/wiki/Generating_set_of_a_group).
But that article is way too confusing to someone who has never taken abstract algebra (like me). So I shall direct you to something that makes slightly more [sense](https://en.wikipedia.org/wiki/Primitive_root_modulo_n).


If you are still lost it is okay. In the context of this problem, where we will end up doing $g^{something} \bmod p$ (as shown in the next function), a generator is *an integer that can be turned into every other integer coprime to p, after doing it to the power of something*. Since we are working with modular arithmetic, specifically mod p, we are working with every number between 1 and p - 1 (0 is not coprime to p). If you wanted to get a specific one of those numbers between 1 and p-1, there exists a number (lets call it a) that you could do g to the power of mod p in order to get that specific number. It just all depends on picking the right number a.


A nice way to see it is with a table. Using mod p = 7 and g = 3
| | |
|---|---|
| g^0  | 1 = 1  |
| g^1  | 3 = 3  |
| g^2  | 9 = 2  |
| g^3  | 27 = 6 |
| g^4  | 81 = 4 |
| g^5| 243 = 5 |
| g^6| 729 = 1 |
| | | 

See, you get every number between 1 and 6 (p-1). It is important to take note that not every number is a generator and that numbers may only be generators in specific moduli. 


## Keys
```python
def key(g, p):
    # generate key info
    a = randint(2, p - 1)
    A = pow(g, a, p)

    return a, A
```
This function generates and returns two numbers. The first is a random number between 2 (inclusive) and p-1 (exclusive). The second is $A = g^a \bmod p$. Since a is a random integer, and g is a generator, we really have no clue as to what A is since it could be *any* number between 1 and p-1 (because as a generator, g can be turned into any number through exponentiation, so by doing it to the power of a random number, you will obtain a random number).

## Encryption Function
```python
def encrypt_setup(p, g, A):
    def encrypt(m):
        k = randint(2, p - 1)
        c1 = pow(g, k, p)
        c2 = pow(A, k, p)
        c2 = (m * c2) % p

        return c1, c2

    return encrypt
```
For this you give it 4 numbers: p (which will be your random prime), g (your generator, aka 2), A, and m. Inside of the function, tt will generate yet another random integer k, and then return back to you **$c1 = g^k \bmod p$, and $c2 = m*A^k \bmod p$**. Keep track of this algebra, it's really important for later on.

## Decryption Function
```python
def decrypt_setup(a, p):
    def decrypt(c1, c2):
        m = pow(c1, a, p)
        m = pow(m, -1, p)
        m = (c2 * m) % p

        return m

    return decrypt
```
Now this is your decryption function. It looks really similar to the encryption function. except now its will return $c2 * c1^{-a} \bmod p$. Although in modular arithmetic negative powers really mean inverses, the algebra will work out the same and it looks a tad prettier than me simply saying "inverse of $c1^a$ times m mod p. 

## It's almost time
```python

def main():
    print("[$] Welcome to Morphing Time")

    g, p = 2, getPrime(512)
    a = randint(2, p - 1)
    A = pow(g, a, p)
    decrypt = decrypt_setup(a, p)
    encrypt = encrypt_setup(p, g, A)
    print("[$] Public:")
    print(f"[$]     {g = }")
    print(f"[$]     {p = }")
    print(f"[$]     {A = }")
```
Welcome to Morphing time! Now all this segment of code does is actually set everything up. It runs a bunch of previous functions (funnily enough not key or setup, even though key and setup's actual code is basically copy-pasted into here which is why I explained it.)
As a quick recap of our numbers: g is the generator 2, p is a prime, and A is $g^a \bmod p$ and can be *anything*. They also give you all of these numbers which you can get through netcat or pwntools.
The decrypt and encryption functions also are given all of these numbers (with no mixups) and at this stage, everything is fine.

## Nothing is fine
```python
    c1, c2 = encrypt(flag)
    print("[$] Eavesdropped Message:")
    print(f"[$]     {c1 = }")
    print(f"[$]     {c2 = }")
```
We have now encrypted the flag (if you want to read the [function](encryption-function) again, m would be the flag) and printed out c1 and c2. Remember that what we noted earlier was that $c1 = g^k \bmod p$, and $c2 = m*A^k \bmod p$. So however shall we get this flag?

## It's Morphing Time
```python
print("[$] Give A Ciphertext (i1, i2) to the Oracle:")
    try:
        i1 = input("[$]     i1 = ")
        i1 = int(i1)
        assert 1 < i1 < p - 1

        i2 = input("[$]     i2 = ")
        i2 = int(i2)
        assert 1 < i2 < p - 1
    except:
        print("!! You've Lost Your Chance !!")
        exit(1)

    print("[$] Decryption of You-Know-What:")
    m = decrypt((c1 * i1) % p, (c2 * i2) % p)
    print(f"[$]     {m = }")
```
This is where the problem gets interesting. You are allowed to give the program two numbers of your choosing, named c1_ and c2_. **I am going to refer to these numbers as i1 and i2 respectively just to guarantee that they will not get confused with c1 and c2**. They will then use decrypt with c1*i1 and c2*i2. The secret behind decryption relies on picking the proper numbers. But how do we do that?
Let's substitute everything with whatever we know. We know $c1 = g^k \bmod p$, and $c2 = m*{A}^{k} \bmod p$, we also know that $A = g^a \bmod p$. so $c2 = m*{g}^{{a}^{k}} \bmod p$ or $c2 = m*g^{ak} \bmod p$. We also know that we run the decryption function returns $c2 * c1^{-a} \bmod p$.

But wait a second, there's a sly trick involved here. The c1 and c2 mentioned like 3 seconds ago were multiplied with i1 and i2. So lets use that. The decryption function really returns $(c2*i2)*{(c1*i1)}^{-a}$. Then we input our other values of c2 and c1 and get $(m*{g}^{ak} * i2)*(g^k * i1)^{-a})$. Now if we were to say that i2 and i1 were 1, then everything would cancel and we would get m (which is our flag).
However, we cannot do that because it checks that i1 and i2 are between 1 and p-1. Looking at the equation we have $(m*g^{ak}*i2)*(g^k*i1)^{-a})$ or $(m)(g^{ak} *i2)*(g^k*i1)^{-a})$. That means we want $(g^{a*k}*i2)*(g^k*i1)^(-a))$ to equal 1. 

Okay we now know our objective. Let's go achieve it. Looking at $(g^{ak}*i2)*(g^k*i1)^{-a}) $ we can rewrite it as $(g^{a*k}*i2)*(g^{-a*k} * i1^{-a}) = g^{ak} * g^{-ak}*i2*i1^{-a}$. Well, $g^{ak}*g^{-ak} = g^{ak-ak} = g^0 = 1$. So $g^{ak}*g^{-ak}*i2*i1^{-a} = i2*i1^{-a}$.

We're almost there. So we have $i2 * (i1)^{-a}$. What numbers do we actually know? Well we know g = 2. They gave us p earlier. They gave us A earlier. We also know A = $g^a$. Wait a second. That seems familier to what we want. If we were to say $i2 = A = g^a$ then we would get $g^a*i1^{-a}$. The final step is to say that i1 = g. Then the expression becomes $g^a*g^{-a}$ which equals 1. 

That's the where all the math leads us. To simply using two numbers that they gave us at the beginning of the question. To clean up all of the horrendous math, all we have to do is give them 2 and whatever number they printed for A and in turn you will receive the number $4207564671745017061459002831657829961985417520046041547841180336049591837607722234018405874709347956760957$. You can simply using the pycryptodome module and do             
```python 
Crypto.Util.number.long_to_bytes(4207564671745017061459002831657829961985417520046041547841180336049591837607722234018405874709347956760957)
``` 
to get the flag (or whatever method to turn integer into bytes) and you will receive the lovely flag:

### ```b'uiuctf{h0m0m0rpi5sms_ar3_v3ry_fun!!11!!11!!}'```





