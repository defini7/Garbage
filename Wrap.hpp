#ifndef WRAP_HPP
#define WRAP_HPP

/*
* Function for wrapping numbers to fit them in range
*/
template <class T>
constexpr T wrap(T value, const T min, const T max);


// Useful macro for defining common functions
#define WRAP_FUNCTION_TITLE(name) \
	template <class TL, class TR> \
	constexpr auto wrap_##name( \
		const TL lhs, \
		const TR rhs, \
		const decltype(lhs + rhs) min, \
		const decltype(lhs + rhs) max) \


// Use that to add your custom operations
#define WRAP_ADD_OPERATION(name, operation) \
	WRAP_FUNCTION_TITLE(name) \
	{ \
		return wrap(lhs operation rhs, min, max); \
	} \


// There are provided some basic operations with 2 numbers
WRAP_FUNCTION_TITLE(add);
WRAP_FUNCTION_TITLE(sub);
WRAP_FUNCTION_TITLE(mul);
WRAP_FUNCTION_TITLE(div);


/*
* Finds short distance between 2 numbers,
* also within the range
*/
WRAP_FUNCTION_TITLE(shortdist);


/*
* Finds shortest difference
* between two numbers,
* that exist within the range
*/
WRAP_FUNCTION_TITLE(shortdiff);


#ifdef WRAP_IMPL
#undef WRAP_IMPL


template <class T>
constexpr T wrap(
	T value,
	const T min,
	const T max)
{
	auto range = max - min;
	while (value < min) value += range;
	while (value > max) value -= range;
	return value;
}


WRAP_ADD_OPERATION(add, +)
WRAP_ADD_OPERATION(sub, -)
WRAP_ADD_OPERATION(mul, *)
WRAP_ADD_OPERATION(div, /)


WRAP_FUNCTION_TITLE(shortdist)
{
	auto a = wrap_sub(lhs, rhs, min, max);
	auto b = wrap_sub(rhs, lhs, min, max);
	return (a > b) ? a : b;
}


WRAP_FUNCTION_TITLE(shortdiff)
{
	auto a = wrap_sub(lhs, rhs, min, max);
	auto b = wrap_sub(rhs, lhs, min, max);
	return (a > b) ? -b : a;
}

#endif

#endif
