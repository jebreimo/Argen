#pragma once
#include <iosfwd>
#include <string>
#include <vector>

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

    /** @brief Member for options -s and --special.
      */
    std::vector<std::string> s = {"Kjakan Gundersen"};


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
        RESULT_ERROR
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
Arguments parse_arguments(int argc, char* argv[], bool autoExit = true);

void write_help_text(std::ostream& stream, unsigned lineWidth = 0);

void write_brief_help_text(std::ostream& stream, unsigned lineWidth = 0);
