"""
JouleLens — Utility Helpers.
Shared formatting functions, score mappings, and region data.
"""

from collections import OrderedDict


def format_joules(j):
    """Smart formatter for Joule values."""
    if j < 0.001:
        return f"{j * 1000:.2f} mJ"
    elif j < 1:
        return f"{j:.3f} J"
    else:
        return f"{j:.2f} J"


def format_currency(usd):
    """Format cost with appropriate precision."""
    if usd < 0.001:
        return f"₹{usd:.6f}"
    elif usd < 1:
        return f"₹{usd:.5f}"
    else:
        return f"₹{usd:.4f}"


def format_co2(grams):
    """Format CO2 emissions with appropriate unit."""
    if grams < 0.001:
        return f"{grams * 1000:.3f} mg CO2"
    elif grams < 1:
        return f"{grams * 1000:.1f} mg CO2"
    elif grams < 1000:
        return f"{grams:.3f} g CO2"
    else:
        return f"{grams / 1000:.3f} kg CO2"


def score_to_color(score):
    colors = {"A": "#00FF88", "B": "#3FB950", "C": "#F0A500", "D": "#FF8C00", "F": "#FF4B4B"}
    return colors.get(score, "#8B949E")


def score_to_label(score):
    labels = {"A": "Excellent", "B": "Good", "C": "Fair", "D": "Poor", "F": "Critical"}
    return labels.get(score, "Unknown")


def score_to_css_class(score):
    return f"score-{score.lower()}" if score in "ABCDF" else "score-c"


def truncate_code(code, max_chars=100):
    if not code:
        return ""
    code = code.strip().replace("\n", " | ")
    if len(code) > max_chars:
        return code[:max_chars] + "..."
    return code


def get_region_options():
    return OrderedDict([
        ("California (CAISO)", "US-CAL-CISO"),
        ("Texas (ERCOT)", "US-TEX-ERCO"),
        ("New York (NYISO)", "US-NY-NYIS"),
        ("Great Britain", "GB"),
        ("Germany", "DE"),
        ("France", "FR"),
        ("India (Southern)", "IN-SO"),
        ("Australia (NSW)", "AU-NSW"),
        ("Japan (Tokyo)", "JP-TK"),
        ("Brazil (South)", "BR-S"),
        ("South Africa", "ZA"),
        ("Singapore", "SG"),
    ])


def get_zone_display_name(zone_code):
    regions = get_region_options()
    for display, code in regions.items():
        if code == zone_code:
            return display
    return zone_code


DEMO_SNIPPETS = {
    "Python": {
        "Demo 1 - Inefficient Loop": '''# Naive prime finder - energy inefficient
def find_primes(n):
    primes = []
    for num in range(2, n):
        is_prime = True
        for i in range(2, num):
            if num % i == 0:
                is_prime = False
        if is_prime:
            primes.append(num)
    return primes

result = find_primes(5000)
print(f"Found {len(result)} primes")
''',
        "Demo 2 - Matrix Multiply": '''import random
def matrix_multiply_naive(size):
    A = [[random.random() for _ in range(size)] for _ in range(size)]
    B = [[random.random() for _ in range(size)] for _ in range(size)]
    C = [[0]*size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(size):
                C[i][j] += A[i][k] * B[k][j]
    return C

result = matrix_multiply_naive(100)
''',
        "Demo 3 - Efficient Fibonacci": '''from functools import lru_cache
@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

results = [fibonacci(i) for i in range(50)]
print(results[-1])
''',
    },
    "C": {
        "Demo 1 - Inefficient Loop": '''#include <stdio.h>
#include <stdlib.h>

// Naive prime finder - energy inefficient
int* find_primes(int n, int* count) {
    int* primes = malloc(n * sizeof(int));
    *count = 0;
    for (int num = 2; num < n; num++) {
        int is_prime = 1;
        for (int i = 2; i < num; i++) {
            if (num % i == 0) {
                is_prime = 0;
            }
        }
        if (is_prime) {
            primes[(*count)++] = num;
        }
    }
    return primes;
}

int main() {
    int count;
    int* result = find_primes(5000, &count);
    printf("Found %d primes\\n", count);
    free(result);
    return 0;
}
''',
        "Demo 2 - Matrix Multiply": '''#include <stdlib.h>

// Naive Matrix Multiplication
void matrix_multiply_naive(int size) {
    double** A = malloc(size * sizeof(double*));
    double** B = malloc(size * sizeof(double*));
    double** C = malloc(size * sizeof(double*));
    for(int i=0; i<size; i++) {
        A[i] = malloc(size * sizeof(double));
        B[i] = malloc(size * sizeof(double));
        C[i] = calloc(size, sizeof(double));
        for(int j=0; j<size; j++) {
            A[i][j] = (double)rand() / RAND_MAX;
            B[i][j] = (double)rand() / RAND_MAX;
        }
    }
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            for (int k = 0; k < size; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

int main() {
    matrix_multiply_naive(100);
    return 0;
}
''',
        "Demo 3 - Efficient Fibonacci": '''#include <stdio.h>

long long cache[100] = {0};

long long fibonacci(int n) {
    if (n < 2) return n;
    if (cache[n] != 0) return cache[n];
    cache[n] = fibonacci(n-1) + fibonacci(n-2);
    return cache[n];
}

int main() {
    long long results[50];
    for (int i = 0; i < 50; i++) {
        results[i] = fibonacci(i);
    }
    printf("%lld\\n", results[49]);
    return 0;
}
'''
    },
    "C++": {
        "Demo 1 - Inefficient Loop": '''#include <iostream>
#include <vector>

// Naive prime finder - energy inefficient
std::vector<int> find_primes(int n) {
    std::vector<int> primes;
    for (int num = 2; num < n; num++) {
        bool is_prime = true;
        for (int i = 2; i < num; i++) {
            if (num % i == 0) {
                is_prime = false;
            }
        }
        if (is_prime) {
            primes.push_back(num);
        }
    }
    return primes;
}

int main() {
    auto result = find_primes(5000);
    std::cout << "Found " << result.size() << " primes" << std::endl;
    return 0;
}
''',
        "Demo 2 - Matrix Multiply": '''#include <vector>
#include <cstdlib>

// Naive Matrix Multiplication
std::vector<std::vector<double>> matrix_multiply_naive(int size) {
    std::vector<std::vector<double>> A(size, std::vector<double>(size));
    std::vector<std::vector<double>> B(size, std::vector<double>(size));
    std::vector<std::vector<double>> C(size, std::vector<double>(size, 0.0));
    
    for(int i=0; i<size; i++) {
        for(int j=0; j<size; j++) {
            A[i][j] = (double)std::rand() / RAND_MAX;
            B[i][j] = (double)std::rand() / RAND_MAX;
        }
    }
    
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            for (int k = 0; k < size; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
    return C;
}

int main() {
    auto result = matrix_multiply_naive(100);
    return 0;
}
''',
        "Demo 3 - Efficient Fibonacci": '''#include <iostream>
#include <unordered_map>
#include <vector>

std::unordered_map<int, long long> cache;

long long fibonacci(int n) {
    if (n < 2) return n;
    if (cache.count(n)) return cache[n];
    cache[n] = fibonacci(n-1) + fibonacci(n-2);
    return cache[n];
}

int main() {
    std::vector<long long> results;
    for (int i = 0; i < 50; i++) {
        results.push_back(fibonacci(i));
    }
    std::cout << results.back() << std::endl;
    return 0;
}
'''
    },
    "Java": {
        "Demo 1 - Inefficient Loop": '''import java.util.ArrayList;
import java.util.List;

public class PrimeFinder {
    // Naive prime finder - energy inefficient
    public static List<Integer> findPrimes(int n) {
        List<Integer> primes = new ArrayList<>();
        for (int num = 2; num < n; num++) {
            boolean isPrime = true;
            for (int i = 2; i < num; i++) {
                if (num % i == 0) {
                    isPrime = false;
                }
            }
            if (isPrime) {
                primes.add(num);
            }
        }
        return primes;
    }

    public static void main(String[] args) {
        List<Integer> result = findPrimes(5000);
        System.out.println("Found " + result.size() + " primes");
    }
}
''',
        "Demo 2 - Matrix Multiply": '''import java.util.Random;

public class MatrixMath {
    public static double[][] matrixMultiplyNaive(int size) {
        Random rand = new Random();
        double[][] A = new double[size][size];
        double[][] B = new double[size][size];
        double[][] C = new double[size][size];
        
        for(int i=0; i<size; i++) {
            for(int j=0; j<size; j++) {
                A[i][j] = rand.nextDouble();
                B[i][j] = rand.nextDouble();
            }
        }
        
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                for (int k = 0; k < size; k++) {
                    C[i][j] += A[i][k] * B[k][j];
                }
            }
        }
        return C;
    }

    public static void main(String[] args) {
        double[][] result = matrixMultiplyNaive(100);
    }
}
''',
        "Demo 3 - Efficient Fibonacci": '''import java.util.HashMap;
import java.util.ArrayList;
import java.util.List;

public class Fib {
    private static HashMap<Integer, Long> cache = new HashMap<>();

    public static long fibonacci(int n) {
        if (n < 2) return n;
        if (cache.containsKey(n)) return cache.get(n);
        long result = fibonacci(n-1) + fibonacci(n-2);
        cache.put(n, result);
        return result;
    }

    public static void main(String[] args) {
        List<Long> results = new ArrayList<>();
        for (int i = 0; i < 50; i++) {
            results.add(fibonacci(i));
        }
        System.out.println(results.get(results.size() - 1));
    }
}
'''
    }
}


def analyze_complexity(code_string, language="Python"):
    """
    Heuristically analyze code string for Time and Space complexity.
    Returns (time_complexity, space_complexity).
    """
    import ast
    import re
    if language != "Python":
        loops = len(re.findall(r'\b(for|while)\s*\(', code_string))
        time_c = "O(1)" if loops == 0 else ("O(N)" if loops == 1 else ("O(N²)" if loops == 2 else "O(N³)"))
        allocs = bool(re.search(r'\b(new|malloc|calloc|realloc|alloc|std::vector|List<)\b', code_string))
        space_c = "O(N)" if allocs else "O(1)"
        return time_c, space_c

    try:
        tree = ast.parse(code_string)
    except Exception:
        return "O(?)", "O(?)"

    class ComplexityVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_loop_depth = 0
            self.max_loop_depth = 0
            self.allocates_memory = False

        def visit_For(self, node):
            self.current_loop_depth += 1
            self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
            self.generic_visit(node)
            self.current_loop_depth -= 1

        def visit_While(self, node):
            self.current_loop_depth += 1
            self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
            self.generic_visit(node)
            self.current_loop_depth -= 1
            
        def visit_ListComp(self, node):
            self.allocates_memory = True
            self.current_loop_depth += 1
            self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
            self.generic_visit(node)
            self.current_loop_depth -= 1

        def visit_DictComp(self, node):
            self.allocates_memory = True
            self.current_loop_depth += 1
            self.max_loop_depth = max(self.max_loop_depth, self.current_loop_depth)
            self.generic_visit(node)
            self.current_loop_depth -= 1

        def visit_List(self, node):
            self.allocates_memory = True
            self.generic_visit(node)

        def visit_Dict(self, node):
            self.allocates_memory = True
            self.generic_visit(node)

        def visit_Set(self, node):
            self.allocates_memory = True
            self.generic_visit(node)
            
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and node.func.attr in ('append', 'extend', 'add', 'update'):
                self.allocates_memory = True
            self.generic_visit(node)

    visitor = ComplexityVisitor()
    visitor.visit(tree)

    if visitor.max_loop_depth == 0:
        time_c = "O(1)"
    elif visitor.max_loop_depth == 1:
        time_c = "O(N)"
    elif visitor.max_loop_depth == 2:
        time_c = "O(N²)"
    elif visitor.max_loop_depth == 3:
        time_c = "O(N³)"
    else:
        time_c = f"O(N^{visitor.max_loop_depth})"

    class RecursionVisitor(ast.NodeVisitor):
        def __init__(self):
            self.has_recursion = False
            self.current_func = None
        
        def visit_FunctionDef(self, node):
            old_func = self.current_func
            self.current_func = node.name
            self.generic_visit(node)
            self.current_func = old_func
            
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and self.current_func == node.func.id:
                self.has_recursion = True
            self.generic_visit(node)

    rec_visitor = RecursionVisitor()
    rec_visitor.visit(tree)
    
    if rec_visitor.has_recursion:
        if visitor.max_loop_depth == 0:
            time_c = "O(2^N)"
        space_c = "O(N)"
    else:
        if visitor.allocates_memory:
            space_c = "O(N)"
        else:
            space_c = "O(1)"

    if time_c == "O(1)" and space_c == "O(N)":
        time_c = "O(N)"
        
    return time_c, space_c
