#include <string>
#include <iosfwd>

namespace Program
{
    enum class ArgumentsResult
    {
        Ok,
        Error,
        Help
    };

    struct Arguments
    {
        int unnamed = {};
        std::string outfile;
        bool exclude = {};

        ArgumentsResult result = ArgumentsResult::Ok;
    };

    enum class AutoTerminateMode
    {
        Never,
        AfterHelp,
        AfterError,
        AfterHelpOrError
    };

    enum class UnknownOptionMode
    {
        Ignore,
        TreatAsError,
        TreatAsArgument
    };

    struct ParserOptions
    {
        ParserOptions();
        ParserOptions(AutoTerminateMode autoTerminateMode);
        ParserOptions(UnknownOptionMode unknownOptionMode);
        ParserOptions(AutoTerminateMode autoTerminateMode,
                      UnknownOptionMode unknownOptionMode);

        AutoTerminateMode autoTerminateMode;
        UnknownOptionMode unknownOptionMode;
    };

    /** @brief Parses the arguments in argv.
      *
      * @param argc The number of arguments in argv, including the name
      *     of the program itself at position 0.
      * @param argv
      * @param help_terminates if true the program automatically terminates
      *     after displaying the help text if the command line contains the
      *     help option.
      */
    Arguments parse_arguments(int argc, char* argv[],
                              ParserOptions options = {});

    void write_help_text(std::ostream& stream);

    void write_synopsis(std::ostream& stream);
}
