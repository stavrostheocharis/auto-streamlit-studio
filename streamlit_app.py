import streamlit as st
from scipy.optimize import minimize
import numpy as np

def main():
    st.title("Optimization App")
    st.write("This app finds the minimum of a function")

    func_type = st.selectbox("Select a function", ["Quadratic", "Exponential"], key="func_type")
    if func_type == "Quadratic":
        def func(x):
            return x**2 + 2*x + 1
    else:
        def func(x):
            return np.exp(x) + 2*x

    init_guess = st.number_input("Initial guess", value=1.0, key="init_guess")

    res = minimize(func, init_guess)

    st.write("Optimization result:")
    st.write(f"Minimum value: {res.fun}")
    st.write(f"Optimal x: {res.x}")

if __name__ == "__main__":
    main()