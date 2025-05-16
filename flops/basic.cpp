// 0.901896 GFLOP/S

#include <iostream>
#include <chrono>
#include <random>

constexpr size_t N = 512;

using real_t = long double;

int main()
{
    float** A = new float* [N];
    float** B = new float* [N];
    float** C = new float* [N];

    for (size_t i = 0; i < N; i++)
    {
        A[i] = new float[N];
        B[i] = new float[N];
        C[i] = new float[N];
    }

    std::mt19937 mt;
    std::uniform_real_distribution<> dst(-1000.0, 1000.0);

    for (size_t i = 0; i < N; i++)
        for (size_t j = 0; j < N; j++)
        {
            A[i][j] = dst(mt);
            B[i][j] = dst(mt);
        }

    auto tp1 = std::chrono::high_resolution_clock::now();

    for (size_t i = 0; i < N; i++)
        for (size_t j = 0; j < N; j++)
        {
            float sum = 0.0f;

            for (size_t k = 0; k < N; k++)
                sum += A[i][k] * B[k][j];

            C[i][j] = sum;
        }

    auto tp2 = std::chrono::high_resolution_clock::now();
    real_t seconds = std::chrono::duration<real_t>(tp2 - tp1).count();

    real_t flops = real_t(2 * N * N * N) / seconds;

    std::cout << std::fixed << flops * 1e-9 << " GFLOP/S" << std::endl;

    for (size_t i = 0; i < N; i++)
    {
        delete[] A[i];
        delete[] B[i];
        delete[] C[i];
    }

    delete[] A;
    delete[] B;
    delete[] C;
}
