// Licensed to the LF AI & Data foundation under one
// or more contributor license agreements. See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership. The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License. You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package indexnode

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	"github.com/milvus-io/milvus-proto/go-api/v2/commonpb"
	"github.com/milvus-io/milvus-proto/go-api/v2/milvuspb"
	"github.com/milvus-io/milvus/internal/proto/indexpb"
	"github.com/milvus-io/milvus/internal/proto/internalpb"
	"github.com/milvus-io/milvus/pkg/util/merr"
	"github.com/milvus-io/milvus/pkg/util/metricsinfo"
)

func TestAbnormalIndexNode(t *testing.T) {
	in, err := NewMockIndexNodeComponent(context.TODO())
	assert.NoError(t, err)
	assert.Nil(t, in.Stop())
	ctx := context.TODO()
	status, err := in.CreateJob(ctx, &indexpb.CreateJobRequest{})
	assert.NoError(t, err)
	assert.ErrorIs(t, merr.Error(status), merr.ErrServiceNotReady)

	qresp, err := in.QueryJobs(ctx, &indexpb.QueryJobsRequest{})
	assert.NoError(t, err)
	assert.ErrorIs(t, merr.Error(qresp.GetStatus()), merr.ErrServiceNotReady)

	status, err = in.DropJobs(ctx, &indexpb.DropJobsRequest{})
	assert.NoError(t, err)
	assert.ErrorIs(t, merr.Error(status), merr.ErrServiceNotReady)

	jobNumRsp, err := in.GetJobStats(ctx, &indexpb.GetJobStatsRequest{})
	assert.NoError(t, err)
	assert.ErrorIs(t, merr.Error(jobNumRsp.GetStatus()), merr.ErrServiceNotReady)

	metricsResp, err := in.GetMetrics(ctx, &milvuspb.GetMetricsRequest{})
	err = merr.CheckRPCCall(metricsResp, err)
	assert.ErrorIs(t, err, merr.ErrServiceNotReady)

	configurationResp, err := in.ShowConfigurations(ctx, &internalpb.ShowConfigurationsRequest{})
	err = merr.CheckRPCCall(configurationResp, err)
	assert.ErrorIs(t, err, merr.ErrServiceNotReady)
}

func TestGetMetrics(t *testing.T) {
	var (
		ctx          = context.TODO()
		metricReq, _ = metricsinfo.ConstructRequestByMetricType(metricsinfo.SystemInfoMetrics)
	)
	in, err := NewMockIndexNodeComponent(ctx)
	assert.NoError(t, err)
	defer in.Stop()
	resp, err := in.GetMetrics(ctx, metricReq)
	assert.NoError(t, err)
	assert.True(t, merr.Ok(resp.GetStatus()))
	t.Logf("Component: %s, Metrics: %s", resp.ComponentName, resp.Response)
}

func TestGetMetricsError(t *testing.T) {
	ctx := context.TODO()

	in, err := NewMockIndexNodeComponent(ctx)
	assert.NoError(t, err)
	defer in.Stop()
	errReq := &milvuspb.GetMetricsRequest{
		Request: `{"metric_typ": "system_info"}`,
	}
	resp, err := in.GetMetrics(ctx, errReq)
	assert.NoError(t, err)
	assert.Equal(t, resp.GetStatus().GetErrorCode(), commonpb.ErrorCode_UnexpectedError)

	unsupportedReq := &milvuspb.GetMetricsRequest{
		Request: `{"metric_type": "application_info"}`,
	}
	resp, err = in.GetMetrics(ctx, unsupportedReq)
	assert.NoError(t, err)
	assert.ErrorIs(t, merr.Error(resp.GetStatus()), merr.ErrMetricNotFound)
}

func TestMockFieldData(t *testing.T) {
	chunkMgr := NewMockChunkManager()

	chunkMgr.mockFieldData(100000, 8, 0, 0, 1)
}
