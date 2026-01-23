import api
import math

def add(a, b):
    return api.add(a, b)
def subtract(a, b):
    return api.subtract(a, b)
def multiply(a, b):
    return api.multiply(a, b)
def divide(a, b):
    return api.divide(a, b)
    if b == 0:
        raise ValueError("Cannot divide by zero.")

def main(num1,num2):
    print(f"{num1} + {num2} = {add(num1,num2)}")
    print(f"{num1} - {num2} = {subtract(num1,num2)}")
    print(f"{num1} * {num2} = {multiply(num1,num2)}")
    print(f"{num1} / {num2} = {divide(num1,num2)}")

def pi():
    return math.pi

if __name__ == "__main__":
    print(f"请不要直接运行此模块或 open calc，请在 main.py 中调用 calc 模块的 main 函数。")