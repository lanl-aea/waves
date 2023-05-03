function main(name)

parser = inputParser;
isText = @(input) isstring(input) || ischar(input);
addRequired(parser, 'name', isText);
parse(parser, name);

file_id = fopen([name '.txt'], 'w');
fprintf(file_id, 'Hello %s!\n', name);
fclose(file_id);

exit;
end
