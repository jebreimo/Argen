CLAPGen - C++ Command-Line Argument Parser-Generator
====================================================

What does it do?
The program takes a plain text file with descriptions of a program's arguments and options and produces C++ source code that parses these options and arguments.

Quick tutorial
--------------
This tutorial demonstrates how to add argument and option parsing to a program.

I'm making a program like the UNIX(R) command whereis, but want to add a couple of extra options. Initially the source code looks like this:

    // whereis.cpp
    #include <iostream>
    
    int main(int argc, char* argv[])
    {
        if (argc != 2)
        {
            std::cerr << "usage: " << argv << " <file name>\n";
            return 1;
        }
        // listFiles(argv[1]); // Lists files matching its argument.
        return 0;
    }

I compile this file with

    c++ whereis.cpp -o whereis

And run it:

    $ ./whereis
    usage: ./whereis <file name>

Now I want to add a couple of options and replace a proper help message when the -h or --help option is given:

    USAGE
        whereis [options] <file name>
    
    Searches the directories in the PATH environment variable for files starting with <file name>.
    
    OPTIONS
    -h, --help                  Show help
    -i PATH, --include=PATH     Include PATHS among the directories searched.
    
To create a parser that parses program's arguments and store them in a convenient structure, and displays the help text when appropriatw it's necessary to add a little markup:

    USAGE
        whereis [options] ${<file name>}$
    
    Searches the directories in the PATH environment variable for files starting with <file name>.
    
    OPTIONS
    ${-h, --help             }$     Show help
    ${-i PATH, --include=PATH}$     Include PATHS among the directories searched.

I run this file through clapgen:

    $ ls
    whereis.cpp whereis
    $ clapgen helptext.txt
    clapgen: Generated ParseArguments.h and ParseArguments.cpp.
    $ ls
    ParseArguments.cpp ParseArguments.h whereis* whereis.cpp

I change whereis.cpp to:

    // whereis.cpp
    #include <iostream>
    #include "ParseArguments.h"
    
    int main(int argc, char* argv[])
    {
        std::unique_ptr<Arguments> args = parse_arguments(argc, argv);
        if (args->parse_arguments_result == Arguments::Result_Ok)
            return 1;
        // listFiles(args->file_name); // Lists files matching its argument.
        return 0;
    }
