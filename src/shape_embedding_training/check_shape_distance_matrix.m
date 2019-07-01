addpath('../');
global_variables;

%% Load shape distance matrix
t_begin = clock;
fprintf('Loading shape distance matrix from \"%s\"...', g_shape_distance_matrix_file_mat);
load(g_shape_distance_matrix_file_mat);
t_end = clock;
fprintf('done (%f seconds)!\n', etime(t_end, t_begin));

nz = nonzeros(shape_distance_matrix);
fprintf('nonzero distances: min=%g, max=%g, mean=%g, std=%g, median=%g\n',min(nz),max(nz),mean(nz),median(nz),std(nz));
shape_distance_matrix_NxN = squareform(shape_distance_matrix);

fprintf('Collecting shapes listed in \"%s\"...\n', g_shape_list_file);
shape_list_fid = fopen(g_shape_list_file);
line = fgetl(shape_list_fid);
image_count = 0;
shape_list = {};
shape_count = 0;
while ischar(line)
    shape_count = shape_count + 1;
    shape_property = strsplit(line, ' ');
    shape_list{shape_count} = shape_property;
    line = fgetl(shape_list_fid);
end
fclose(shape_list_fid);
if shape_count ~= size(shape_distance_matrix_NxN, 1)
    error('wrong shape_count or matrix dimensions');
end

%% The diagonal should be zero, so add identity
sd = shape_distance_matrix_NxN + eye(size(shape_distance_matrix_NxN));
[i,j] = find(~sd);
equal_count = 0;
for n = 1:size(i)
    if i(n) > j(n)
        equal_count = equal_count + 1;
        %%disp([i(n),j(n),shape_distance_matrix_NxN(i(n),j(n)),shape_list{i(n)},shape_list{j(n)}]);
        fprintf('%s == %s\n', char(shape_list{i(n)}(2)),char(shape_list{j(n)}(2)));
    end
end

fprintf('found %d identical shapes\n', equal_count);
