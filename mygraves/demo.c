int add(int a, int b) {
    return a + b;
}

int square(int x) {
    return x * x;
}

int compute(int x) {
    int y = square(x);
    return add(y, 10);
}

int main() {
    int result = compute(5);
    return result;
}
