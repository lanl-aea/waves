function main(name)
    % Print 'Hello name!' to a file named ``name``.txt
    %
    % :param name: string or character array name
    %
    % Written against the following Matlab products:
    %
    % ======================================= ======= ============= =======
    % Name                                    Version ProductNumber Certain
    % --------------------------------------- ------- ------------- -------
    % MATLAB                                  9.13     1            true
    % ======================================= ======= ============= =======
    %
    % Table build reference: https://www.mathworks.com/help/matlab/ref/matlab.codetools.requiredfilesandproducts.html
    %
    % Docstring formatted for sphinxcontrib-matlabdomain: https://pypi.org/project/sphinxcontrib-matlabdomain/

    parser = inputParser;
    isText = @(input) isstring(input) || ischar(input);
    addRequired(parser, 'name', isText);
    parse(parser, name);

    extension = '.txt';
    fileName = append(name, extension);
    fileID = fopen(fileName, 'w');
    fprintf(fileID, 'Hello %s!\n', name);
    fclose(fileID);

    exit;

end
