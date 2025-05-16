// 2.426772 GFLOP/S

#include <iostream>
#include <chrono>
#include <random>
#include <thread>
#include <vector>

constexpr size_t N = 1024;

using real_t = long double;

float** A = new float* [N];
float** B = new float* [N];
float** C = new float* [N];

// The idea: split calculating into blocks,
// each block has a fixed amount of cells to calculate

constexpr size_t BLOCK_SIZE = 128;
constexpr size_t REGIONS_WIDTH = N / BLOCK_SIZE;
constexpr size_t REGIONS_COUNT = REGIONS_WIDTH * REGIONS_WIDTH;

std::vector<std::thread> threadpool;
std::atomic<size_t> readycount(0);

void create_thread(size_t sx, size_t sy)
{
    threadpool.push_back(std::thread([&]
        {
            for (size_t oi = 0; oi < BLOCK_SIZE; oi++)
                for (size_t oj = 0; oj < BLOCK_SIZE; oj++)
                {
                    float sum = 0.0f;

                    for (size_t k = 0; k < N; k++)
                        sum += A[sy + oi][k] * B[k][sx + oj];

                    C[sy + oi][sx + oj] = sum;
                }

            ++readycount;
        }));
}

void calc()
{
    threadpool.reserve(REGIONS_COUNT);

    for (size_t i = 0; i < N; i += BLOCK_SIZE)
        for (size_t j = 0; j < N; j += BLOCK_SIZE)
            create_thread(i, j);
}

int main()
{
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

    calc();
    while (readycount != REGIONS_COUNT);

    auto tp2 = std::chrono::high_resolution_clock::now();
    real_t seconds = std::chrono::duration<real_t>(tp2 - tp1).count();

    real_t flops = real_t(2 * N * N * N) / seconds;

    std::cout << std::fixed << flops * 1e-9 << " GFLOP/S" << std::endl;

    for (auto& t : threadpool)
        t.join();

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
