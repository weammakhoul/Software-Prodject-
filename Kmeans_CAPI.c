#include <Python.h>
#define PY_SSIZE_T_CLEANS
#include <stdio.h>
#include <malloc.h>
#include <math.h>
#include <stdlib.h>

static PyObject* kmeans_capi(PyObject *self, PyObject *args);
static double **parse_arrays(PyObject* _list, int num_row, int num_col);
static PyObject *pseudo_main(PyObject* Py_data, PyObject* Py_centroids, int N, int d, int K, int MAX_ITER); //static?


/* the wrapping function for the pseudo_main - parses PyObjects */
static PyObject* kmeans_capi(PyObject *self, PyObject *args){
    
    PyObject *data, *centroids;
    int rows, dim, K, MAX_ITER;
    if(!PyArg_ParseTuple(args, "OOiiii", &data, &centroids, &rows, &dim, &K, &MAX_ITER)){
        return NULL;
    }
    return Py_BuildValue("O", pseudo_main(data, centroids, rows, dim, K, MAX_ITER));
}

/* functino that parses the data and puts them in arrays */
static double **parse_arrays(PyObject* _list, int num_row, int num_col) {
    
    int i, j;
    Py_ssize_t Py_i, Py_j;
    double **parsed_data;
    parsed_data = malloc(num_row * sizeof(double*));
    assert(parsed_data!=NULL);
    PyObject* item; PyObject* num;
    for (i = 0; i < num_row; i++) {
        Py_i = (Py_ssize_t)i;
        parsed_data[Py_i] = malloc(num_col * sizeof(double));
        assert(parsed_data[Py_i]!=NULL);
        item = PyList_GetItem(_list, Py_i);
        if (!PyList_Check(item)){ /* Skips non-lists */
            continue;
        }
        for (j = 0; j < num_col; j++) {
            Py_j = (Py_ssize_t)j;
            num = PyList_GetItem(item, Py_j);
            if (!PyFloat_Check(num)) continue; /* Skips non-floats */
            parsed_data[Py_i][Py_j] = PyFloat_AsDouble(num);
        }
    }return parsed_data;
}

/* this array tells python what methods this module has */
static PyMethodDef capiMethods[] = {
	
        {"fit",
                (PyCFunction) kmeans_capi,
                     METH_VARARGS,
                	PyDoc_STR("calculates the centroids using kmeans algorithm")},
        {NULL, NULL, 0, NULL}
};

/* This struct initiates the module using the above definition. */
static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "mykmeanssp",           //name of module
        NULL,                   //module documentation
        -1,                     //size of per-interpreter
        capiMethods
};

/* Module Creation */
PyMODINIT_FUNC
PyInit_mykmeanssp(void) {
    PyObject *m;
    m = PyModule_Create(&moduledef);
    if (!m) {
        return NULL;
    }
    return m;
}

double dist(double *point1, double *point2, int dimension) {

    int i;
    double sum = 0;
    for (i = 0; i < dimension; i++) {
        sum += pow((point1[i]-point2[i]), 2);
    }

    sum = pow(sum, 0.5);
    return sum;
}

int mindist(int k, int dimension, double **centroids_list, double *point) {

    double min = dist(centroids_list[0], point, dimension);
    int index = 0;
    int j;
    for (j = 1; j < k; j++) {
        double distance = dist(centroids_list[j], point, dimension);
        if (distance < min) {
            min = distance;
            index = j;
        }
    }
    return index;
}

void Init(int k, int dimension, int *count_array, double **sum_array) {
    int i, j;
    for (i = 0; i < k; i++) {
        count_array[i] = 0;
        for (j = 0; j < dimension; j++) {
            sum_array[i][j] = 0;
        }
    }
}

void clustering(int k, int rows, int dimension, int *count_array,
                double **sum_array, double **DataPoints, double **centroids_list) {
    int i;
    int j;
    int index;
    for (i = 0; i < rows; i++) {
        index = mindist(k, dimension, centroids_list, DataPoints[i]);
        count_array[index]++;
        for (j = 0; j < dimension; j++) {
            sum_array[index][j] += DataPoints[i][j];
        }
    }

    for (i = 0; i < k; i++) {
        for (j = 0; j < dimension; j++) {
            sum_array[i][j] = sum_array[i][j] / count_array[i];
        }
    }
}

int calculate_delta(int k, int dimension, double **centroids_list, double **sum_array) {
    double distance;
    int i, j;
    int bol = 1;
    for (i = 0; i < k; i++) {
        distance = dist(centroids_list[i], sum_array[i], dimension);
        if (distance > 0.01) {
            bol = 0;
            break;
        }
    }

    for (i = 0; i < k; i++) {
        for (j = 0; j < dimension; j++) {
            centroids_list[i][j] = sum_array[i][j];
        }
    }
    return bol;
}


/* initializing data and running the algorithm */
static PyObject *pseudo_main(PyObject* Py_data, PyObject* Py_centroids, int num_rows, int dim, int K, int MAX_ITER){
    
    PyObject *lst_centroids, *vec, *num;
    int dimension = dim;
    int rows = num_rows;
    int i, j;
    double **centroids_list;
    double **sum_array;
    double **DataPoints;
    int *count_array;
    int delta = 0;
    int iter;
    
    /* initialising centroids, data, cSum, cNum, data_index*/
    DataPoints = parse_arrays(Py_data, rows, dimension);
    centroids_list = parse_arrays(Py_centroids, K, dimension);

    sum_array = malloc(sizeof(double *) * K);
    for (i = 0; i<K; i++) {
        sum_array[i] = (double *) malloc((dimension) * sizeof(double));
    }

    count_array = (int *) malloc(sizeof(int) * K);

    iter = 0;
    while(delta==0 && iter < MAX_ITER) {
        Init(K, dimension, count_array, sum_array);
        clustering(K, rows, dimension, count_array, sum_array, DataPoints, centroids_list);
        delta = calculate_delta(K, dimension, centroids_list, sum_array);
        iter++;
    }

    lst_centroids = PyList_New(K);
    if (!lst_centroids){
        return NULL;
    }
    for(i=0; i<K; i++){
        vec = PyList_New(dimension);
        if (!vec){
            return NULL;
        }
        for (j = 0; j < dimension; j++) {
            num = PyFloat_FromDouble(centroids_list[i][j]);
            if (!num) {
                Py_DECREF(vec);
                return NULL;
            }PyList_SET_ITEM(vec, j, num);
        }PyList_SET_ITEM(lst_centroids, i, vec);
    }

    for(i=0 ; i<K ; i++){
        free(centroids_list[i]);
        free((sum_array[i]));
    }
    free(centroids_list);
    for(i=0 ; i<rows ; i++){
        free(DataPoints[i]);
    }
    free(DataPoints);
    free(sum_array);
    free(count_array);

    return lst_centroids;
}
