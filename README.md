Argen - Generates C++ code for parsing for options and arguments
==================================================================

An easy to use, yet very sophisticated generator of command line argument parsers for C++ programs.

### What it does
It takes what is essentilly a text file with the help text of a program - the one shown when the program is executed with the help option (typically -h, --help or /?) - and creates C++ code that parses the arguments and options, checks them for errors and converts them to their intended types. All the programmer has to do is include the generated files in the project or makefile, and call the generated parser function, typically from main.

### Features
* **Multiple kinds of options**. Posix dash options, DOS/Windows slash options, double-dash options, and virtually any other kind.
* **Multi-value options**. Multiple instances of the same option are added to a list. Comma-separated values are supported, in fact almost any separator can be used.
* **Extremely flexible help text format**.
* **Clever deduction of argument and option properties**.
* **Platform independent**. Both generator and generated files have been tested on Linux, Mac OS X and Windows.
* **No dependencies**. Generated code does not require any other libraries than the standard library

### Requirements
* The generator requires Python 2.7 or 3.3 (it may work, but has not been tested with other versions).
* The generated files requires a compiler with at least some C++11-support (lambdas, auto, unique_ptr). It's been tested with Visual Studio 2010 and 2012 (Windows), Clang 3.3 (Mac) and gcc 4.8 (Linux).

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

Run it through argen:

    $ ls
    helptext.txt    main.cpp
    $ argen helptext.txt
    argen: generated ParseArguments.h and ParseArguments.cpp
    $ ls
    helptext.txt    main.cpp    ParseArguments.h    ParseArguments.cpp

Compile the program (UNIX)

    $ c++ -std=c++11 main.cpp ParseArguments.cpp -o ParseArguments

Compile the program (Visual Studio):

    $ cl /EHsc main.cpp ParseArguments.cpp
Run the command with the help option:

    $ ./ParseArguments -h
    ParseArguments [options] <file> [message ...]
    
    Does something.
    
    OPTIONS
    -h, --help
        Prints this help message
    -s W,H, --size=W,H
        Set the image size to Width,Height (default is 800,600).
    -i PATH, --include=PATH     Something

Run the command with options and arguments:

    $ ./test -size=100,80 -i /usr/include -i /usr/local/include text.txt
    Size is 100x80
    Includes:
      /usr/include
      /usr/local/include
    File is text.txt
    Messages:
      Hello world!

FAQ
---

### How can I use || (i.e. or) in my conditions?

Reference for argen options
=============================

Options for formatting the help text
------------------------------------

### --align=NUM
Set the width of the initial whitespace when the help text for an option is split across multiple lines. argen normally detects this width automatically, but it sometimes gets it wrong, and then the correct value can be set with this option.

### --width=NUM
Set the line width.

Options for setting the names of files, functions and classes
-------------------------------------------------------------

### --class=NAME
Set the name of the generated class to NAME. The default is "Arguments".

### --cpp=SUFFIX
Set the file name suffix for the generated source file. The default is "cpp".

### --file=NAME
Set the name of the generated header and source files. The default is "ParseArguments".

### --function=NAME
Set the name of the generated function. The default is "parse_arguments".

### --hpp=SUFFIX
Set the file name suffix for the generated header file. The default is "hpp".

### --namespace=NAME
Set the namespace for the generated code. Multi-level namespaces are specified using `::` to separate each name (e.g. `--namespace=jeb::application`)

Miscellaneous options
---------------------

### --debug
Parses the help text file and dumps the internal structures to stdout. This option is only for debugging the deducted property values.

### --parenthesis=PARENS
This option should only be used if the actual help text must contain either `${` or `$}`. The option sets the sequence of characters that marks the start and end of an argument or option definition. The PARENS value must consist of both the start and the end sequence, separated by a single space. As space is also used to separate arguments it's necessary to enclose the entire option in double-quotes (e.g. `argen "--parenthesis=@< >@" ...`).

### --test
Include a main-function in the source file to test the argument parser.

Reference for option and argument properties
============================================

### Action

    Action: C++-CODE

The action is performed once for each time the option or argument is encountered. It is executed after the member has been assigned a value.

### Argument

    Argument: NAME

*Argument* is primarily used in combination with the *Flags* property to specify that an option requires an argument. Unlike *Text*, it's not possible to specify option arguments with *Flags* property's value, hence this property.

#### Example
This creates a non-standard option "out-file" that takes an argument "FILE":

    ${out-file FILE|flags: out-file | argument: FILE}$  Sets the name of the output file

The help text for this option will be:

    out-file FILE  Sets the name of the output file

### Condition

    Condition: C++-CONDITION

The "Condition" property is an extra check that is performed after the option or argument has been assigned its value.
 
#### Example

    ${-l, --lines           | member: mode | value: "lines"}$
    ${-r, --rectangles      | member: mode | value: "rectangles"}$
    ${-c, --circles         | member: mode | value: "circles"}$
    ${-d NUM, --diameter=NUM| condition: $mode$ == "circles"}$
    ${-l NUM, --length=NUM  | condition: $mode$ == "lines" || $mode$ == "rectangles"}$
    ${-w NUM, --width=NUM   | condition: $mode$ == "rectangles"}$

### ConditionMessage

    ConditionMessage: TEXT

### Count

    Count: VALUE or MIN..MAX

Determines the number of values the member for an option or argument can hold. If the maximum count is greater than one, the member becomes a vector of *ValueType*. The count-value should be either a single integer (setting the minimum and maximum to the same value) or two integers separated by two dots (i.e. minimum..maximum). The default for options is 0..1 and for arguments it's 1. When using the two dots it's actually possible to leave out one or both integers. If the first integer is left out, the minimum becomes 0. If the second integer is left out, there is no upper limit to the number of values.

#### Example 1
    ${-a VALUE --alpha=VALUE | count: 1 }$ A mandatory option

#### Example 2
    ${-b FILE --bravo=FILE | count: 0..}$ A list with 0 or more values.

The above line adds a member named "bravo" of type `std::vector\<std::string\>` to the generated struct.

#### Example 3
    ${-c NUM --charlie=NUM | count: 3..5}$ An option that must be given 3 to 5 times.

### Default

    Default: VALUE

The default value for the option or argument's member. If this property is not specified, it uses the default constructor for the member's type (see the *ValueType* property). To set the default value for options and arguments that accept delimited values (see *Delimiter* below), use the delimiter to separate individual values.
    
#### Examples
This creates an int-option with default-value 10:

    ${-a NUM --alpha=NUM | Default: 10}$

This creates an optional argument of comma-separated strings. If the argument isn't given on the command line its values will be "/foo" and "/bar".

    ${[PATHS]| Delimiter: , | Default: "foo","bar"}$ 

### Delimiter

    Delimiter: CHARACTER

A single character (e.g. comma or colon) used to separate values in a list. If an argument or the value part of an option contains a comma (e.g. `--point=X,Y`), the delimiter automatically becomes comma. The delimited values must all have the same type; it's for instance not possible for the first value to be an int and the second be a double. Whitespace characters can not be used as delimiters.

#### Example
The following line creates a member (std::vector\<std::string\>) with each colon-separated value given in PATHS:

    ${-i PATHS, --include=PATHS | Delimiter: :} A colon-separated list of paths to be searched

The following line results in a member (std::vector\<double\>) that accepts two comma-separated values. The comma in the option's value makes it unnecessary to explicitly state the delimiter:

    ${-o X,Y --origin=X,Y| Default: 0.0,0.0}$

### DelimiterCount

    DelimiterCount: VALUE or MIN..MAX

Specifies the number of delimiters an argument or option-value must contain. The number of actual values is always one greater than the number of delimiters. The format is the same as for the *Count* property: a single number for a fixed number of separators and the double-dot syntax for a variable number of values. The default is 0.. which means any number of delimiters are allowed. Howver the DelimiterCount automatically becomes the number of delimter characters if the argument or option's value contains one or more of them.

#### Example
The DelimiterCount automatically becomes 1 on the following line:

    ${-s ROWSxCOLS| Delimiter: x | Default: 1x1}$

Here the mandatory argument must contain 2 to 5 delimiters (i.e. 3 to 6 values):

    ${<dimensions>| Delimiter: , | DelimiterCount: 2..5 | Type: int}$

### Flags

    Flags: NAME ...

Explicitly set the flags for an option. The automatic detection of options and arguments require that options consist of at least two characters and start with a dash `-` or a slash `/`. To create other options - for instance a single-character option - it's necessary to use this property. If there are multiple flags for the same option the flags must separated by whitespace. It's not possible specify the option argument with the Flags property, to do so the `Argument` option must also be used.

#### Examples

    ${a, average| Flags: a average}$ Calculate the average.
    
Creates an option that can be invoked with two different flags, "a" and "average". The text in front of "|" doesn't start with a dash or slash and is therefore assumed to be an argument. By using the flags property, the initial text is ignored and the space separated words after flags are used instead. As no other properties are specified, it becomes a boolean option that is false by default and true when the option is given.

### Include

    Include: FILE

Adds an include directive to the generated header file. Used in combination with the ValueType property to make the generated include file include the header file that defines the type. The property value must be enclosed in "" or \<>.
    
#### Examples

    ${--population=N | ValueType: int64_t | Include: <cstdint>}$

    ${<date>| ValueType: Date | Include: "Date.h" |
      Values: [Date(1900, 1, 1)..Date::now()>}$

### IncludeCPP

    IncludeCPP: FILE

Add an include directive to the generated cpp-file. *IncludeCPP* is used in combination with the `Default` and `Values` properties.
    
#### Examples

    ${-a NUM, --alpha=NUM| ValueType: int | Default: INT_MAX | IncludeCPP: <limits.h>}$

Creates a member *alpha* of type *int* which has the default value *INT_MAX*. INT_MAX is a constant defined in the standard C header file "*limits.h*".

### Index

    Index: NUMBER

The zero-based index of the argument. This property allows out-of-order definition of arguments. The *Index* property only applies to arguments (i.e. non-options), and 

#### Example

    ${<file>}$
    ${<destination file>}$
    ${[files...]| Index: 1}$

### Member

    Member: NAME

The name of the member variable

### PostCondition

    PostCondition: C++-CONDITION

### PostConditionMessage

    PostConditionMessage: TEXT

### Text

    Text: OPTION-DEFINITION or ARGUMENT-DEFINITION

#### Example 2:
To create an option that is case-insensitive and accepts both a slash and a dash prefix, but is listed in the help text as just "/A".

    ${/A NUM| Text: /A NUM /a -A -a | Default: 0}$ Set the alpha-level.

### Type

    Type: TYPE

TYPE must be one of the following words:
* `Help`: specifies that this is a help option. Options automatically become help options if their `Member` property is "help" (this is for instance true if the option is `/?` or `--help`). When the generated *parse_arguments* function encounters a help-option it writes the help message to stdout and returns immediately without parsing any remaining options or arguments.
* `Info`: use this on options that make the program display some piece of information and ignore the requires certain options and arguments for its normal operation, but also other arguments (e.g. an option for displaying the program's version or a list of available services).
* *MultiValue*:
* *Value*
* *List*    values are stored in a vector
* *Final*   the option marks the end of all options, all remaining arguments are treated as arguments even if they start with a dash. POSIX-compliant program should make "--" the final option. There won't be a members for final options in the Arguments struct.

### Value

    Value: VALUE

This only applies to flags, i.e. options that don't take an argument. The value that will be assigned (or appended) to the variable if the flag is given.

### Values

    Values: VALUE or MIN..MAX ...

The legal values for the argument or option. The same set of legal values applies to all values when "type" is "list" or "multi-value".

### ValueType

    ValueType: TYPE

This is the type of the values of the option or argument. argen doesn't enforce any restrictions on the types, however the generated code is unlikely to compile unless the type is among the bool, integer or floating point types, or std::string. If the type or typedef used isn't defined in `<cstddef>` or `<string>`,  it is necessary to customize the generated file. Strings must be of type "string" or "std::string", in the former case the type is silently translated to "std::string". See the *Include* property to see how to include the file defining a custom type.
#### Requirements for custom types:
* There must be a -input-operator (`>>`) for streams.
* Unless *Default* is specified it must have a default-constructor.
* If the *Values* property is used it must support the `==` operator if *Values* contains any single values, and the `<` operator if it contains any ranges.
* If argen is run with the --test option there must also be a output-operator (`<<`) for streams.