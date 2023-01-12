function main(name)

file_id = fopen([name '.txt'], 'w');
fprintf(file_id, 'Hello %s!\n', name);
fclose(file_id);

exit;
end
