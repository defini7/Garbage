#ifndef FIXED_POINT_HPP
#define FIXED_POINT_HPP

#include <cstdint>

template <class T1, class T2, size_t dp>
struct fixed
{
	constexpr fixed() = default;
	constexpr fixed(double d);

	constexpr operator double() const;

	constexpr fixed& operator=(const fixed& f) = default;

	constexpr fixed operator-() const;
	constexpr fixed operator+(const fixed& f) const;
	constexpr fixed operator-(const fixed& f) const;
	constexpr fixed operator*(const fixed& f) const;
	constexpr fixed operator/(const fixed& f) const;

	T1 n = (T1)0;

private:
	static constexpr fixed form(T1 n);

};

using fp16 = fixed<int32_t, int64_t, 16>;
using fp4 = fixed<int8_t, int16_t, 4>;

constexpr fp16 operator ""_fp16(long double n);
constexpr fp4 operator ""_fp4(long double n);

#ifdef FIXED_POINT_IMPL
#undef FIXED_POINT_IMPL

template <class T1, class T2, size_t dp>
constexpr fixed<T1, T2, dp>::fixed(double d)
{
	n = T1(d * double(1 << dp) + (d >= 0 ? 0.5 : -0.5));
}

template <class T1, class T2, size_t dp>
constexpr fixed<T1, T2, dp>::operator double() const
{
	return (((double)n - 0.5 >= 0.0) ? ((double)n - 0.5) : ((double)n + 0.5)) / double(1 << dp);
}

template <class T1, class T2, size_t dp>
constexpr fixed<T1, T2, dp>& fixed<T1, T2, dp>::operator=(const fixed& f) = default;

template <class T1, class T2, size_t dp>
constexpr fixed<T1, T2, dp> fixed<T1, T2, dp>::operator-() const { return form(-n); }

template <class T1, class T2, size_t dp>
constexpr fixed<T1, T2, dp> fixed<T1, T2, dp>::operator+(const fixed<T1, T2, dp>& f) const { return form(n + f.n); }

template <class T1, class T2, size_t dp>
constexpr fixed<T1, T2, dp> fixed<T1, T2, dp>::operator-(const fixed<T1, T2, dp>& f) const { return form(n - f.n); }

template <class T1, class T2, size_t dp>
constexpr fixed<T1, T2, dp> fixed<T1, T2, dp>::operator*(const fixed<T1, T2, dp>& f) const
{
	return form(((T2)n * (T2)f.n) >> dp);
}

template <class T1, class T2, size_t dp>
constexpr fixed<T1, T2, dp> fixed<T1, T2, dp>::operator/(const fixed& f) const
{
	return form(((T2)n << dp) / (T2)f.n);
}

template <class T1, class T2, size_t dp>
constexpr fixed<T1, T2, dp> fixed<T1, T2, dp>::form(T1 n)
{
	fixed<T1, T2, dp> f;
	f.n = n;
	return f;
}

constexpr fp16 operator ""_fp16(long double n) { return fp16(n); }
constexpr fp4 operator ""_fp4(long double n) { return fp4(n); }

#endif

#endif
