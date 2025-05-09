// https://en.wikipedia.org/wiki/Fixed-point_arithmetic

#include <type_traits>

template <class low_t, class high_t, high_t bits>
struct fixed
{
    // We will use low_t as a type for representing fp number as an integer
    // and high_t must be as twice large as low_t because we will cast integer of type low_t
    // to high_t to perform multiplication and division

    static_assert(std::is_integral_v<low_t>, "low_t is not an integral type");
    static_assert(std::is_integral_v<high_t>, "high_t is not an integral type");

    constexpr fixed() = default;
    constexpr fixed(double v)
    {
        // First of all represent double as an int by multiplying v by 2^bits,
        // the more bits we have the more precision we get
        value = v * double(1 << bits) + (bits >= 0.0 ? 0.5 : -0.5);
    }

    constexpr operator double() const
    {
        // Convert fixed point number back to floating point one
        return (double)value / double(1 << bits);
    }

    constexpr fixed operator-() { return { -value }; }

    constexpr fixed operator+(const fixed& f) { return { value + f.value }; }
    constexpr fixed operator-(const fixed& f) { return { value - f.value }; }

    constexpr fixed& operator+=(const fixed& f) { value += f.value; return *this; }
    constexpr fixed& operator-=(const fixed& f) { value -= f.value; return *this; }

    constexpr fixed& operator++() { value++; return *this; }
    constexpr fixed& operator--() { value--; return *this; }

    constexpr fixed& operator++(int) { fixed old = *this; value++; return old; }
    constexpr fixed& operator--(int) { fixed old = *this; value--; return old; }

    constexpr fixed operator*(const fixed& f)
    {
        return { ((high_t)value * (high_t)f.value) >> bits };
    }

    constexpr fixed operator/(const fixed& f)
    {
        return { ((high_t)value << bits) / (high_t)f.value };
    }

    constexpr fixed& operator*=(const fixed& f)
    {
        value = ((high_t)value * (high_t)f.value) >> bits;
        return *this;
    }

    constexpr fixed& operator/=(const fixed& f)
    {
        // Notice that we changed the order of operations:
        // we power it and then divide so the precision is preserved
        value = ((high_t)value << bits) / (high_t)f.value;
        return *this;
    }

    low_t value;

};

using fixed4 = fixed<int8_t, int16_t, 4>;
using fixed8 = fixed<int16_t, int32_t, 8>;
using fixed16 = fixed<int32_t, int64_t, 16>;

//     2^3 2^2 2^1 2^0 | 2^(-1) 2^(-2) 2^(-3) 2^(-4)
// 2.6  0   0   1   0  |   1      0      0      1    <- notice that there is a carry left
// 4.3  0   1   0   0  |   0      1      0      0    <- and here too
//
// 2.6 + 4.3 = 00101001 + 01000100 = 01101101 = 109 = 6.9375 (according to MSVC++)
// f32   f32     base2      base2      base2   base10  f32
//                                              ^
// because of the carry the result is not quite accurate and instead of 109 here must be 110

int main()
{
    constexpr fixed4 a(2.6);
    constexpr fixed4 b(4.3);

    constexpr double c = double(a + b);
    constexpr double d = double(a - b);
    constexpr double e = double(a * b);
    constexpr double f = double(a / b);
}
