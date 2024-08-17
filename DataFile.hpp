#ifndef DATA_FILE_HPP
#define DATA_FILE_HPP

#pragma region license
/***
*	BSD 3-Clause License
	Copyright (c) 2021, 2022, 2023, 2024 Alex
	All rights reserved.
	Redistribution and use in source and binary forms, with or without
	modification, are permitted provided that the following conditions are met:
	1. Redistributions of source code must retain the above copyright notice, this
	   list of conditions and the following disclaimer.
	2. Redistributions in binary form must reproduce the above copyright notice,
	   this list of conditions and the following disclaimer in the documentation
	   and/or other materials provided with the distribution.
	3. Neither the name of the copyright holder nor the names of its
	   contributors may be used to endorse or promote products derived from
	   this software without specific prior written permission.
	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
	AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
	IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
	DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
	FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
	DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
	SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
	CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
	OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
	OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
***/
#pragma endregion

#pragma region includes

#include <iostream>
#include <string>
#include <cstring>
#include <unordered_map>
#include <functional>
#include <fstream>
#include <list>
#include <stack>

#pragma endregion

class DataFile
{
public:
	DataFile() = default;
	~DataFile() = default;

public:
	void SetString(const std::string& sValue, size_t nIndex = 0);
	std::string GetString(size_t nIndex = 0) const;

	void SetInt(long long nValue, size_t nIndex = 0);
	long long GetInt(size_t nIndex = 0) const;

	void SetDecimal(long double dValue, size_t nIndex = 0);
	long double GetDecimal(size_t nIndex = 0) const;

	void SetBool(bool bValue, size_t nIndex = 0);
	bool GetBool() const;

	bool HasProperty(const std::string& sName) const;

	DataFile& operator[](const std::string& sKey);

	static bool Write(DataFile& dataFile, const std::string& sFileName);
	static bool Read(DataFile& dataFile, const std::string& sFileName);

	size_t CountValues() const;
	size_t CountObjects() const;

	std::vector<std::string>& GetValues();

private:
	std::vector<std::string> m_vValues;

	std::vector<std::pair<std::string, DataFile>> m_vObjects;
	std::unordered_map<std::string, size_t>		  m_mapObjects;

};

#ifdef DATA_FILE_IMPL
#undef DATA_FILE_IMPL

void DataFile::SetString(const std::string& sValue, size_t nIndex)
{
	if (nIndex >= m_vValues.size())
		m_vValues.resize(nIndex + 1);

	m_vValues[nIndex] = sValue;
}

std::string DataFile::GetString(size_t nIndex) const
{
	return m_vValues[nIndex];
}

void DataFile::SetInt(long long nValue, size_t nIndex)
{
	SetString(std::to_string(nValue), nIndex);
}

long long DataFile::GetInt(size_t nIndex) const
{
	return std::stoll(GetString(nIndex));
}

void DataFile::SetDecimal(long double dValue, size_t nIndex)
{
	SetString(std::to_string(dValue), nIndex);
}

long double DataFile::GetDecimal(size_t nIndex) const
{
	return std::stold(GetString(nIndex));
}

void DataFile::SetBool(bool bValue, size_t nIndex)
{
	SetString(std::to_string((int)bValue), nIndex);
}

bool DataFile::GetBool() const
{
	return (bool)std::stoll(GetString());
}

bool DataFile::HasProperty(const std::string& sName) const
{
	return m_mapObjects.count(sName) > 0;
}

DataFile& DataFile::operator[](const std::string& sKey)
{
	if (m_mapObjects.count(sKey) == 0)
	{
		m_mapObjects[sKey] = m_vObjects.size();
		m_vObjects.push_back({ sKey, DataFile() });
	}

	return m_vObjects[m_mapObjects[sKey]].second;
}

bool DataFile::Write(DataFile& dataFile, const std::string& sFileName)
{
	std::function<void(std::ofstream&, DataFile&, size_t)> Write = [&](std::ofstream& os, DataFile& df, size_t tabs)
		{
			auto AddTabs = [&]()
				{
					for (size_t i = 0; i < tabs; i++)
						os << '\t';
				};

			for (auto& obj : df.m_vObjects)
			{
				AddTabs();

				if (obj.second.m_vObjects.empty())
				{
					os << obj.first << " = ";

					auto& values = obj.second.m_vValues;
					for (size_t i = 0; i < values.size(); i++)
					{
						os << values[i];

						if (i == values.size() - 1)
							os << ";\n";
						else
							os << ", ";
					}
				}
				else
				{
					os << obj.first << "\n";

					AddTabs();
					os << "{\n";

					Write(os, obj.second, tabs + 1);

					AddTabs();
					os << "}\n";
				}
			}
		};

	std::ofstream file(sFileName);

	if (!file.is_open())
		return false;

	Write(file, dataFile, 0);
	file.close();

	return true;
}

bool DataFile::Read(DataFile& dataFile, const std::string& sFileName)
{
	auto Trim = [](std::string& s)
		{
			s.erase(0, s.find_first_not_of(" \t\n\r\f\v"));
			s.erase(s.find_last_not_of(" \t\n\r\f\v") + 1);
		};

	std::ifstream file(sFileName);

	if (!file.is_open())
		return false;

	std::string sFieldName, sFieldValue;

	std::stack<std::reference_wrapper<DataFile>> stack;
	stack.push(dataFile);

	while (!file.eof())
	{
		std::string sLine;
		std::getline(file, sLine);

		if (!sLine.empty())
			Trim(sLine);

		sLine = sLine.substr(0, sLine.find_first_of('#'));

		if (!sLine.empty())
		{
			size_t i = sLine.find_first_of('=');

			if (i == std::string::npos)
			{
				if (sLine.front() == '{')
					stack.push(stack.top().get()[sFieldName]);
				else
				{
					if (sLine.back() == '}')
						stack.pop();
					else
						sFieldName = sLine;
				}
			}
			else
			{
				sFieldName = sLine.substr(0, i);
				Trim(sFieldName);

				sFieldValue = sLine.substr(i + 1, sLine.length());
				Trim(sFieldValue);

				bool bQuotes = false;
				std::vector<std::string> vecTokens = { "" };

				for (const auto& c : sFieldValue)
				{
					if (c == '\"')
						bQuotes = !bQuotes;
					else
					{
						if (bQuotes)
							vecTokens.back() += c;
						else
						{
							if (c == ';')
							{
								for (size_t idx = 0; idx < vecTokens.size(); idx++)
								{
									Trim(vecTokens[idx]);
									stack.top().get()[sFieldName].SetString(vecTokens[idx], idx);
								}

								vecTokens.clear();
							}
							else if (c == ',')
								vecTokens.push_back({});
							else
								vecTokens.back() += c;
						}
					}
				}

				if (!vecTokens.empty())
				{
					for (size_t j = 0; j < vecTokens.size(); j++)
					{
						Trim(vecTokens[j]);
						stack.top().get()[sFieldName].SetString(vecTokens[j], j);
					}

					vecTokens.clear();
				}
			}
		}
	}

	file.close();

	return true;
}

size_t DataFile::CountValues() const
{
	return m_vValues.size();
}

size_t DataFile::CountObjects() const
{
	return m_vObjects.size();
}

std::vector<std::string>& DataFile::GetValues()
{
	return m_vValues;
}

#endif


#endif
