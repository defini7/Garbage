#ifndef ITER_TOOLS_HPP
#define ITER_TOOLS_HPP

#include <algorithm>
#include <coroutine>
#include <optional>
#include <functional>

namespace itertools
{
	template<typename T>
	struct generator
	{
		struct promise_type;
		using handle_type = std::coroutine_handle<promise_type>;

		struct promise_type
		{
			T value;
			std::exception_ptr exception;

			generator<T> get_return_object();

			std::suspend_always initial_suspend();
			std::suspend_always final_suspend() noexcept;

			void unhandled_exception();

			template<std::convertible_to<T> From>
			std::suspend_always yield_value(From&& from);

			void return_void();
		};

		handle_type handle;

		generator(handle_type h);
		generator(const generator&) = delete;
		~generator();

		explicit operator bool();
		T operator()();

	private:
		bool m_Full = false;

		void fill();
	};

	template <class T, class TIter, class TFunc>
	generator<T> accumulate(const TIter begin, const TIter end, TFunc func = std::plus<T>(), std::optional<T> initial = {});

	template <class T, class TIter, class TContainer = std::vector<T>>
	generator<TContainer> batched(const TIter begin, const TIter end, size_t length);

	template <class T, class TIter>
	generator<T> chain(const TIter begin, const TIter end);

	template <class TIter, class TContainer>
	generator<TContainer> combinations(const TIter begin, const TIter end, size_t length);

	template <class T, class TIter1, class TIter2>
	generator<T> compress(const TIter1 begin1, const TIter1 end1, const TIter2 begin2, const TIter2 end2);

	template <class T, class TIter>
	generator<T> drop_while(const TIter begin, const TIter end, std::function<bool(const T&)> predicate);

	template <class T, class TIter>
	generator<T> filter_false(const TIter begin, const TIter end, std::function<bool(const T&)> predicate = [](const T n) { return n; });

#ifdef ITER_TOOLS_IMPL
#undef ITER_TOOLS_IMPL

	template <class T>
	generator<T> generator<T>::promise_type::get_return_object()
	{
		return generator(handle_type::from_promise(*this));
	}

	template <class T>
	std::suspend_always generator<T>::promise_type::initial_suspend() { return {}; }

	template <class T>
	std::suspend_always generator<T>::promise_type::final_suspend() noexcept { return {}; }

	template <class T>
	void generator<T>::promise_type::unhandled_exception()
	{
		exception = std::current_exception();
	}

	template <class T>
	template <std::convertible_to<T> From>
	std::suspend_always generator<T>::promise_type::yield_value(From&& from)
	{
		value = std::forward<From>(from);
		return {};
	}

	template <class T>
	void generator<T>::promise_type::return_void() {}

	template <class T>
	generator<T>::generator(handle_type h) : handle(h) {}

	template <class T>
	generator<T>::~generator() { handle.destroy(); }

	template <class T>
	generator<T>::operator bool()
	{
		fill();
		return !handle.done();
	}

	template <class T>
	T generator<T>::operator()()
	{
		fill();
		m_Full = false;
		return std::move(handle.promise().value);
	}

	template <class T>
	void generator<T>::fill()
	{
		if (!m_Full)
		{
			handle();

			if (handle.promise().exception)
				std::rethrow_exception(handle.promise().exception);

			m_Full = true;
		}
	}

	template <class T, class TIter, class TFunc>
	generator<T> accumulate(const TIter begin, const TIter end, TFunc func, std::optional<T> initial)
	{
		T total = initial.value_or((T)0);
		TIter current = begin;

		if (!initial.has_value())
		{
			if (current == end)
				co_return;

			total = *(current++);
		}

		co_yield total;

		for (TIter it = current; it != end; it++)
		{
			total = func(total, *it);
			co_yield total;
		}
	}

	template <class T, class TIter, class TContainer>
	generator<TContainer> batched(const TIter begin, const TIter end, size_t length)
	{
		if (length < 1)
			co_return;

		TContainer batch;

		for (TIter it = begin; it != end; it++)
		{
			batch.insert(batch.end(), *it);

			if (batch.size() == length)
			{
				co_yield batch;
				batch.clear();
			}
		}
	}

	template <class T, class TIter>
	generator<T> chain(const TIter begin, const TIter end, size_t length)
	{
		for (TIter it = begin; it != end; it++)
			for (auto it1 = it->begin(); it1 != it->end(); it1++)
				co_yield *it1;
	}

	template <class TContainer, class TIter>
	generator<TContainer> combinations(const TIter begin, const TIter end, size_t length)
	{
		size_t size = std::distance(begin, end);

		if (length > size)
			co_return;

		TContainer comb;
		std::vector<int> indicies(size);
		std::fill(indicies.begin(), indicies.begin() + length, 1);

		do
		{
			size_t i = 0;
			for (TIter it = begin; it != end; it++, i++)
			{
				if (indicies[i] != 0)
					comb.insert(comb.end(), *it);
			}

			co_yield comb;
			comb.clear();
		}
		while (std::prev_permutation(indicies.begin(), indicies.end()));
	}

	template <class T, class TIter1, class TIter2>
	generator<T> compress(const TIter1 begin1, const TIter1 end1, const TIter2 begin2, const TIter2 end2)
	{
		TIter1 cur1 = begin1;
		TIter2 cur2 = begin2;

		for (; cur1 != end1 && cur2 != end2; cur1++, cur2++)
		{
			if (*cur2)
				co_yield *cur1;
		}
	}

	template <class T, class TIter>
	generator<T> drop_while(const TIter begin, const TIter end, std::function<bool(const T&)> predicate)
	{
		TIter cur = begin;

		for (; cur != end; cur++)
		{
			if (!predicate(*cur))
			{
				co_yield *(cur++);
				break;
			}
		}

		for (; cur != end; cur++)
			co_yield *cur;
	}

	template <class T, class TIter>
	generator<T> filter_false(const TIter begin, const TIter end, std::function<bool(const T&)> predicate)
	{
		for (TIter cur = begin; cur != end; cur++)
		{
			if (!predicate(*cur))
				co_yield *cur;
		}
	}

#endif
}

#endif
