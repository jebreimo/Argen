CLAPGen - A code generator for C++ Command Line Argument Parsers
================================================================

An easy to use, yet very sophisticated generator of command line argument parsers for C++ programs.

### What it does
It takes what is essentilly a text file with the help text of a program - the one shown when the program is executed with the help option (typically -h, --help or /?) - and creates C++ code that parses the arguments and options, checks them for errors and converts them to their intended types. All the programmer has to do is include the generated files in the project or makefile, and call the generated parser function, typically from main.

### Features
* Handles virtually any kind of option, in particular those starting wit a dash (-), doube-dash (--) or slash (/).
* Handles multi-value options (when multiple instances of the same option should produce a list of values).
* Handles comma-separated values. In fact any single character can be used as separator.
* An extremely flexible help text format.
* Platform independent. Both generator and generated files have been tested on Linux, Mac OS X, Windows, 
* Generated code has no dependencies apart from the standard library

### Requirements
* The generator requires Python 2.7 or 3.3 (it may work, but hasn't been tested on other versions).
* The generated files requires a compiler with at least some C++11-support (lambdas and auto). It's been tested with Visual Studio 2010 and 2012 (Windows), Clang 3.3 (Mac) and gcc 4.8 (Linux).

### A quick example
In this example I assume there is a program draw_message that creates a 
A help text typed into a file helptext.txt:

    %prog% [options] ${<file>}$ ${[message ...]| Default: "Hello world!"}$
    
    Does something.
    
    OPTIONS
    ${-h, --help}$
        Prints this help message
    ${-s W,H, --size=W,H| Default: 800,600}$
        Set the image size to Width,Height (default is 800,600).
    ${-i PATH, --include=PATH}$
        Something

And a C++ file main.cpp:

    #include "ParseArguments.hpp"

    int main(int argc, char* argv[])
    {
        auto args = parse_arguments(argc, argv);
        if (args->parse_arguments_result > Arguments::RESULT_OK)
            return args->parse_arguments_result;
        std::cout << "Size is " << args->size[0] << "x" << args->size[1]
                  << "\nIncludes:\n";
        for (auto it = begin(args->include); it != end(args->include); ++it)
            std::cout << "  " << *it << "\n";
        std::cout << "File is " << args->file << "\nMessages:\n"
        for (auto it = begin(args->message); it != end(args->message); ++it)
            std::cout << "  " << *it << "\n";
        return 0;
    }

Run it through clapgen:

    $ ls
    helptext.txt    main.cpp
    $ clapgen helptext.txt
    clapgen: generated ParseArguments.h and ParseArguments.cpp
    $ ls
    helptext.txt    main.cpp    ParseArguments.h    ParseArguments.cpp
    $ c++ -std=c++11 main.cpp ParseArguments.cpp -o test

Run the command:

    $ ./test -h
    test [options] <file> [message ...]
    
    Does something.
    
    OPTIONS
    -h, --help
        Prints this help message
    -s W,H, --size=W,H
        Set the image size to Width,Height (default is 800,600).
    -i PATH, --include=PATH     Something

    $ ./test -size=100,80 -i /usr/include -i /usr/local/include text.txt
    Size is 100x80
    Includes:
      /usr/include
      /usr/local/include
    File is text.txt
    Messages:
      Hello world!

Reference for option and argument properties
--------------------------------------------

### Argument
Is used in combination with the *Flags* property to specify that an option requires an argument. Unlike *Text*, it's not possible to specify option arguments with *Flags* property's value, hence this property.

#### Example
This creates a non-standard option "out-file" that takes an argument "FILE":

    ${out-file FILE|flags: out-file | argument: FILE}$  Sets the name of the output file

The help text for this option will be:

    out-file FILE  Sets the name of the output file
    
### Count
Determines the number of values the member for an option or argument can hold. If the maximum count is greater than one, the member becomes a vector of *ValueType*. The count-value should be either a single integer (setting the minimum and maximum to the same value) or two integers separated by two dots (i.e. minimum..maximum). The default for options is 0..1 and for arguments it's 1. When using the two dots it's actually possible to leave out one or both integers. If the first integer is left out, the minimum becomes 0. If the second integer is left out, there is no upper limit to the number of values.

#### Example
This adds a member of type std::vector\<std::string\> to the generated struct:

    ${-a VALUE --alpha=VALUE | count: 1 }$ A mandatory option
    ${-b FILE --bravo=FILE | count: 0..}$ A list with 0 or more values.
    ${-c NUM --charlie=NUM | count: 3..5}$ An option that must be given 3 to 5 times.

### Default
The default value for the option or argument's member. If this property is not specified, it uses the default constructor for the member's type (see the *ValueType* property). To set the default value for options and arguments that accept delimited values (see *Delimiter* below), use the delimiter to separate individual values, each value.
    

#### Examples
This creates an int-option with default-value 0.

    ${-a NUM --alpha=NUM | Default: 10}$

This creates an optional argument of comma-separated strings. If the argument isn't given on the command line its values will be "/foo" and "/bar".

    ${[PATHS]| Delimiter: , | Default: "foo","bar"}$ 

### Delimiter
A single character (e.g. comma or colon) used to separate values in a list. If an argument or the value part of an option contains a comma (e.g. `--point=X,Y`), the delimiter automatically becomes comma. The delimited values must all have the same type; it's for instance not possible for the first value to be an int and the second be a double. Whitespace characters can not be used as delimiters.

#### Example
The following line creates a member (std::vector\<std::string\>) with each colon-separated value given in PATHS:

    ${-i PATHS, --include=PATHS | Delimiter: :} A colon-separated list of paths to be searched

The following line results in a member (std::vector\<double\>) that accepts two comma-separated values. The comma in the option's value makes it unnecessary to explicitly state the delimiter:

    ${-o X,Y --origin=X,Y| Default: 0.0,0.0}$

### DelimiterCount
Specifies the number of delimiters an argument or option-value must contain. The number of actual values is always one greater than the number of delimiters. The format is the same as for the *Count* property: a single number for a fixed number of separators and the double-dot syntax for a variable number of values. The default is 0.. which means any number of delimiters are allowed. Howver the DelimiterCount automatically becomes the number of delimter characters if the argument or option's value contains one or more of them.

#### Example
The DelimiterCount automatically becomes 1 on the following line:

    ${-s ROWSxCOLS| Delimiter: x | Default: 1x1}$

Here the mandatory argument must contain 2 to 5 delimiters (i.e. 3 to 6 values):

    ${<dimensions>| Delimiter: , | DelimiterCount: 2..5 | Type: int}$

### Flags

### Include

    ${<date>| ValueType: Date | Include: "Date.h" |
      Values: [Date(1900, 1, 1)..Date::now()]}$

### Index

### Member
The name of the member variable

### Name
The name of the value that will be used in error messages and also the name of the member unless "member" is also specified (any characters in the name that are illegal in member names are replaced with underscores).

### Text

### Type
    Help
    Info
    MultiValue
    Value
    List    values are stored in a vector
    Final   the option marks the end of all options, all remaining arguments are treated as arguments even if they start with a dash. POSIX-compliant program should make "--" the final option. There won't be a members for final options in the Arguments struct.

### Value
This only applies to flags, i.e. options that don't take an argument. The value that will be assigned (or appended) to the variable if the flag is given.

### Values
The legal values for the argument or option. The same set of legal values applies to all values when "type" is "list" or "multi-value".

### ValueType
This is the type of the values of the option or argument. clapgen doesn't enforce any restrictions on the types, however the generated code is unlikely to compile unless the type is among the bool, integer or floating point types, or std::string. If the type or typedef used isn't defined in \<cstddef\>, \<cstdint\> or \<string\>, it is necessary to customize the generated file. Strings must be of type "string" or "std::string", in the former case the type is silently translated to "std::string".

There must be a \>\>-operator for input-streaming the type. If the *Values* property is used, the comparison-operators should be defined. See the *Include* property to see how to include the file defining a custom type.