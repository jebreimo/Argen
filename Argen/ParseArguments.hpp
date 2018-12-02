//****************************************************************************
// Copyright © 2018 Jan Erik Breimo. All rights reserved.
// Created by Jan Erik Breimo on 2018-12-02.
//
// This file is distributed under the BSD License.
// License text is included with the source distribution.
//****************************************************************************
#pragma once
#include <cstdint>
#include <iosfwd>
#include <string>
#include <tuple>
#include <vector>

namespace Foo { namespace Bar
{
    /** @brief The result returned by parse_arguments
      */
    struct Arguments
    {
        /** @brief Returns true if parse_arguments_result is RESULT_OK, false otherwise.
          */
        explicit operator bool() const
        {
            return parse_arguments_result == Result::RESULT_OK;
        }

        /** @brief Member for argument unnamed.
          */
        int unnamed = {};

        /** @brief Member for argument <test name>.
          */
        std::vector<std::string> test_name = {};

        /** @brief Member for argument <the-list>.
          */
        std::vector<std::string> the_list = {};

        /** @brief Member for argument <out-file>.
          */
        std::vector<std::string> out_file = {};

        /** @brief Member for options -e and --exclude.
          */
        bool exclude = {};

        /** @brief Member for options -h and --help.
          */
        bool help = {};

        /** @brief Member for options -l and --log-file.
          */
        std::string log_file = {};

        /** @brief Member for options -q, --quiet, -v and --verbose.
          */
        bool verbose = {};

        /** @brief Member for option --version.
          */
        bool version = {};

        /** @brief Member for option --info.
          */
        bool info = {};

        /** @brief Member for option --junit.
          */
        bool junit = {};

        /** @brief Member for option --text.
          */
        bool text = {};

        /** @brief Member for option --fulltext.
          */
        bool fulltext = {};

        /** @brief Member for options -f and --file.
          */
        std::string file = {};

        /** @brief Member for option --host.
          */
        std::string host = {};

        /** @brief Member for options --ting and --tang.
          */
        std::vector<double> ting = {};

        /** @brief Member for option --foo.
          */
        std::vector<int> foo = {};

        /** @brief Member for option -@.
          */
        std::tuple<int, int, int> at = {0, 2, 4};

        /** @brief Member for options --flag and --antiflag.
          */
        bool flag = true;

        /** @brief Member for option --size.
          */
        std::tuple<int, int> size = {800, 600};

        /** @brief Member for options --cuboid, --rect and --line.
          */
        std::vector<int> cuboid = {};

        /** @brief Member for options -% and --percentage.
          */
        int percentage = 50;

        /** @brief Member for options -s and --special.
          */
        std::vector<std::string> s = {"Kjakan Gundersen"};

        /** @brief Member for option -n.
          */
        std::tuple<double, double> n = {};

        /** @brief Member for option -p.
          */
        std::tuple<double, double, double> p = {};

        /** @brief Member for options -m and --month.
          */
        std::vector<unsigned> month = {};

        /** @brief Member for option --string.
          */
        std::string string = "Two words";

        /** @brief Member for option --kjell.
          */
        int kjell = {};

        /** @brief Member for options -i, --include and --sysinclude.
          */
        std::vector<std::string> include = {};

        /** @brief Member for option --stygg.
          */
        uint64_t stygg = {};

        /** @brief Member for options -u and --user.
          */
        std::vector<std::tuple<std::string, int>> user = {};

        /** @brief Member for option -.
          */
        std::string bar = {};

        /** @brief Member for option -z.
          */
        bool z = {};


        enum Result
        {
            /** @brief parse_arguments parsed the arguments successfully.
              */
            RESULT_OK,
            /** @brief There are invalid or missing options or arguments.
              *
              * An error message has been displayed. The option and argument
              * members of this struct can not be relied upon.
              */
            RESULT_ERROR,
            /** @brief The --help option was given.
              */
            OPTION_help,
            /** @brief The --version option was given.
              */
            OPTION_version,
            /** @brief The --info option was given.
              */
            OPTION_info,
            /** @brief The --version2 option was given.
              */
            OPTION_version2
        };

        /** @brief The exit status of parse_arguments.
          *
          * This member should always be checked before any of the other members
          * are read.
          */
        Result parse_arguments_result = RESULT_OK;

        /** This member is reserved for internal use in parse_arguments.
          *
          * It's always nullptr.
          */
        struct MemberCounters* reserved_for_internal_use = nullptr;
    };

    /** @brief Parses the arguments in @a argv.
      *
      * @param argc the number of values in argv.
      * @param argv the arguments (an array of char-strings).
      * @returns an instance of Arguments with values in
      *     accordance with the parsed arguments. If @a argc is 0 the
      *     returned value is a nullptr.
      */
    Arguments parse_arguments(int argc, char* argv[], bool auto_exit = true);

    void write_help_text(std::ostream& stream, unsigned line_width = 0);

    void write_brief_help_text(std::ostream& stream, unsigned line_width = 0);
}}


inline bool foo_bar(Foo::Bar::Arguments& arguments, const std::string& argument)
{
    return true;
}