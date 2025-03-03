#=============================================================================
# Copyright (c) 2019-2021, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#=============================================================================

##############################################################################
# - build cuml bench executable ----------------------------------------------

if(BUILD_CUML_BENCH)
  # (please keep the filenames in alphabetical order)
  add_executable(${CUML_CPP_BENCH_TARGET}
    sg/arima_loglikelihood.cu
    sg/dbscan.cu
    sg/kmeans.cu
    sg/linkage.cu
    sg/main.cpp
    sg/rf_classifier.cu
    # FIXME: RF Regressor is having an issue where the tests now seem to take
    # forever to finish, as opposed to the classifier counterparts!
    # sg/rf_regressor.cu
    sg/svc.cu
    sg/svr.cu
    sg/umap.cu
    sg/fil.cu
  )

  target_compile_options(${CUML_CPP_BENCH_TARGET}
        PRIVATE "$<$<COMPILE_LANGUAGE:CXX>:${CUML_CXX_FLAGS}>"
                "$<$<COMPILE_LANGUAGE:CUDA>:${CUML_CUDA_FLAGS}>"
  )

  target_link_libraries(${CUML_CPP_BENCH_TARGET}
    PUBLIC
      cuml::${CUML_CPP_TARGET}
      benchmark::benchmark
      raft::raft
      $<IF:$<BOOL:${Treelite_ADDED}>,treelite::treelite_static,treelite::treelite>
      $<IF:$<BOOL:${Treelite_ADDED}>,treelite::treelite_runtime_static,treelite::treelite_runtime>
  )

  target_include_directories(${CUML_CPP_BENCH_TARGET}
    PRIVATE
      $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../src_prims>
  )
endif()

##############################################################################
# - build prims bench executable ----------------------------------------------

if(BUILD_CUML_PRIMS_BENCH)
  # (please keep the filenames in alphabetical order)
  add_executable(${PRIMS_BENCH_TARGET}
    prims/add.cu
    prims/distance_cosine.cu
    prims/distance_exp_l2.cu
    prims/distance_l1.cu
    prims/distance_unexp_l2.cu
    prims/fused_l2_nn.cu
    prims/gram_matrix.cu
    prims/main.cpp
    prims/make_blobs.cu
    prims/map_then_reduce.cu
    prims/matrix_vector_op.cu
    prims/permute.cu
    prims/reduce.cu
    prims/rng.cu)

  target_compile_options(${PRIMS_BENCH_TARGET}
        PRIVATE "$<$<COMPILE_LANGUAGE:CXX>:${CUML_CXX_FLAGS}>"
                "$<$<COMPILE_LANGUAGE:CUDA>:${CUML_CUDA_FLAGS}>"
  )

  target_link_libraries(${PRIMS_BENCH_TARGET}
    PUBLIC
      cuml
      CUDA::cublas
      benchmark::benchmark
      raft::raft
      $<IF:$<BOOL:${Treelite_ADDED}>,treelite::treelite_static,treelite::treelite>
      $<IF:$<BOOL:${Treelite_ADDED}>,treelite::treelite_runtime_static,treelite::treelite_runtime>
  )

  target_include_directories(${PRIMS_BENCH_TARGET}
    PRIVATE
      $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../src_prims>
      $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
  )
endif()
