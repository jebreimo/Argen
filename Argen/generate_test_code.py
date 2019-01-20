# -*- coding: UTF-8 -*-
# ===========================================================================
# Copyright © 2018 Jan Erik Breimo. All rights reserved.
# Created by Jan Erik Breimo on 2018-08-13.
#
# This file is distributed under the BSD License.
# License text is included with the source distribution.
# ===========================================================================
import templateprocessor


class TestCodeGenerator(templateprocessor.Expander):
    def __init__(self, session):
        super().__init__()
        self._session = session

    def namespace(self, *args):
        return self._session.code_properties.namespace

    def has_tuples(self, *args):
        return self._session.code_properties.has_tuples

    def has_vectors(self, *args):
        return self._session.code_properties.has_vectors

    def write_members(self, *args):
        result = []
        for member in self._session.members:
            result.append("WRITE_VALUE(%s);" % member.name)
        return result


def generate_test_code(session):
    return templateprocessor.make_lines(TEST_TEMPLATE,
                                        TestCodeGenerator(session))


TEST_TEMPLATE = """\
#ifdef ARGEN_MAIN
#include <iostream>

[[[IF has_tuples]]]
namespace aux
{
    template<std::size_t...>
    struct seq
    {};
    
    template<std::size_t N, std::size_t... Is>
    struct gen_seq : gen_seq<N-1, N-1, Is...>
    {};
    
    template<std::size_t... Is>
    struct gen_seq<0, Is...> : seq<Is...>
    {};
    
    template<class Ch, class Tr, class Tuple, std::size_t... Is>
    void print_tuple(std::basic_ostream<Ch,Tr>& os, Tuple const& t, seq<Is...>)
    {
        using swallow = int[];
        (void)swallow {
            0,
            (void(os << (Is == 0 ? "" : ", ") << std::get<Is>(t)), 0)...
            };
    }
}

template<class Ch, class Tr, class... Args>
auto operator<<(std::basic_ostream<Ch, Tr>& os, std::tuple<Args...> const& t)
    -> std::basic_ostream<Ch, Tr>&
{
  os << "(";
  aux::print_tuple(os, t, aux::gen_seq<sizeof...(Args)>());
  return os << ")";
}

[[[ENDIF]]]
template <typename T>
void write_value(std::ostream& stream, const char* label, const T& value)
{
    stream << label << ": " << value << "\\n";
}

[[[IF has_vectors]]]
template <typename T>
void write_value(std::ostream& stream, const char* label, const std::vector<T>& vec)
{
    for (size_t i = 0; i < vec.size(); ++i)
    stream << label << "[i]: " << vec[i] << "\\n";
}

[[[ENDIF]]]
#define WRITE_VALUE(name) write_value(std::cout, #name, args.name)

int main(int argc, char* argv[])
{
    auto args = parse_arguments(argc, argv);
    WRITE_VALUE(parse_arguments_result);
    [[[write_members]]]
    return 0;
}
#endif
"""
