addpath('../');
global_variables;

%% Load shape distance matrix
t_begin = clock;
fprintf('Loading shape distance matrix from \"%s\"...', g_shape_distance_matrix_file_mat);
load(g_shape_distance_matrix_file_mat);
t_end = clock;
fprintf('done (%f seconds)!\n', etime(t_end, t_begin));

%% Compute shape embedding space
t_begin = clock;
fprintf('Computing shape embedding space, it takes for a while...');
%% options = statset('Display', 'iter', 'MaxIter', 128);
options = statset('Display', 'iter', 'MaxIter', 256);

%% There may be very similar shapes in the dataset, although it was curated, e.g.:
%% 03001627 69e591a9769e03012c528d33bca1ac2 == 03001627 61d29e8133da0b58d1fd43e2bf80195
%% 03001627 c6e46dc0afd8b9fdd722b8781cb9911 == 03001627 6e1fbf46f1d0fb73d8cc7a9b2448f97
%% 03001627 74625aaed8902197f51f77a6d7299806 == 03001627 6e7455e21a6668a7f51f77a6d7299806
%% We set their distance to 1/100 of the smallest nonzero distance,
%% because the 'sammon' criterion requires strictly positive off-diagonal elements.
%% Here are some sample stats on chair distances (synset =03001627):
%% min=0.000172949, max=53.1886, mean=32.2377, std=3.92785, median=32.6227
smallvalue = min(nonzeros(shape_distance_matrix)) / 100;
shape_distance_matrix(shape_distance_matrix <= 0) = smallvalue;
shape_distance_matrix(1:1+size(shape_distance_matrix,1):end) = 0

[shape_embedding_space, stress, disparities] = mdscale(shape_distance_matrix, g_shape_embedding_space_dimension, 'criterion', 'sammon', 'options', options); 
t_end = clock;
fprintf('done (%f seconds)!\n', etime(t_end, t_begin));

%% Save embedding space
t_begin = clock;
fprintf('Save shape embedding space to \"%s\"...', g_shape_embedding_space_file_mat);
save(g_shape_embedding_space_file_mat, 'shape_embedding_space', '-v7.3');
dlmwrite(g_shape_embedding_space_file_txt, shape_embedding_space, 'delimiter', ' ');
t_end = clock;
fprintf('done (%f seconds)!\n', etime(t_end, t_begin));

exit;
