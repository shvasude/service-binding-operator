package steps

import (
	"fmt"
	"strings"
	"testing"

	"github.com/redhat-developer/service-binding-operator/test/examples/util"
	"github.com/stretchr/testify/require"

	"github.com/getgauge-contrib/gauge-go/gauge"
)

var (
	operatorsNS  = "openshift-operators"
	operatorName = "service-binding-operator"
	appNS        = "service-binding-demo"

	nodeJSApp = "https://github.com/pmacik/nodejs-rest-http-crud"
	appName   = "nodejs-rest-http-crud"

	clusterAvailable = false

	pkgManifest                      = "db-operators"
	bckSvc                           = "postgresql-operator"
	dbName                           = "db-demo"
	sbr                              = ""
	podNameSBO, podNameBackingSvcOpr string
)

var exampleName string

var _ = gauge.Step("Set example directory <exampleName>", func(t *testing.T) {
	examplePath := fmt.Sprintf("%s/%s", util.GetExamplesDir(), exampleName)
	util.SetDir(examplePath)
	res := strings.TrimSpace(util.Run("pwd").Stdout())
	require.Equal(t, examplePath, res)
})

var _ = gauge.Step("Get oc status", func(t *testing.T) {
	result := util.Run("oc", "status")
	require.Equal(t, 0, result.ExitCode)
	clusterAvailable = true
})
