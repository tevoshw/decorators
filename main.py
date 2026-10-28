def A(func):
    def wrapper(a, b):
        print(f'Starting A')
        result = func(a, b)
        print(f'Finishing A')
        return result
    return wrapper

def B(func):
    def wrapper(a, b):
        print(f'Starting B')
        result = func(a, b)
        print(f'Finishing B')
        return result
    return wrapper

@A
@B
def main(a, b):
    return a + b

print(main(2, 5))


"""
A -> B -> main

A func is called and receive the arg:
    - func: In this case will be B()

B func is called and receive the arg:
    - func: In this case will be main()

So the logic it's

1. A printing
2. A calls func(): B()
3. B func starting and print
4. B calls main()
5. main() starting and print
6. returns to B() and finishing print
7. return to A()d and finishing print
8. executes stop

"""