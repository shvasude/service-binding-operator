package servicebindingrequest

import (
	"testing"

	"github.com/redhat-developer/service-binding-operator/pkg/apis/apps/v1alpha1"
	"github.com/redhat-developer/service-binding-operator/pkg/log"
	"github.com/redhat-developer/service-binding-operator/pkg/testutils"
	"github.com/stretchr/testify/require"
	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"sigs.k8s.io/controller-runtime/pkg/controller"
	"sigs.k8s.io/controller-runtime/pkg/event"
	"sigs.k8s.io/controller-runtime/pkg/handler"
	"sigs.k8s.io/controller-runtime/pkg/predicate"
	"sigs.k8s.io/controller-runtime/pkg/reconcile"
	"sigs.k8s.io/controller-runtime/pkg/source"
)

func TestSBRControllerBuildSBRPredicate(t *testing.T) {
	// keep the predicate around
	pred := buildSBRPredicate(log.NewLog("test-log"))

	// the expected behavior is that every create event triggers a reconciliation
	t.Run("create", func(t *testing.T) {
		if got := pred.Create(event.CreateEvent{}); !got {
			t.Errorf("newSBRPredicate() = %v, want %v", got, true)
		}
	})

	// update exercises changes that should or not trigger the reconciliation
	t.Run("update", func(t *testing.T) {
		sbrA := &v1alpha1.ServiceBindingRequest{
			Spec: v1alpha1.ServiceBindingRequestSpec{
				BackingServiceSelector: &v1alpha1.BackingServiceSelector{
					GroupVersionKind: metav1.GroupVersionKind{Group: "test", Version: "v1alpha1", Kind: "TestHost"},
					ResourceRef:      "",
				},
			},
		}
		sbrB := &v1alpha1.ServiceBindingRequest{
			Spec: v1alpha1.ServiceBindingRequestSpec{
				BackingServiceSelector: &v1alpha1.BackingServiceSelector{
					GroupVersionKind: metav1.GroupVersionKind{Group: "test", Version: "v1", Kind: "TestHost"},
					ResourceRef:      "",
				},
			},
		}

		tests := []struct {
			name string
			want bool
			a    runtime.Object
			b    runtime.Object
		}{
			{name: "same-spec", want: false, a: sbrA, b: sbrA},
			{name: "changed-spec", want: true, a: sbrA, b: sbrB},
		}
		for _, tt := range tests {
			t.Run(tt.name, func(t *testing.T) {
				if got := pred.Update(event.UpdateEvent{ObjectOld: tt.a, ObjectNew: tt.b}); got != tt.want {
					t.Errorf("newSBRPredicate() = %v, want %v", got, tt.want)
				}
			})
		}
	})

	// delete verifies that SBRs will be reconciled prior to its deletion
	t.Run("delete", func(t *testing.T) {
		tests := []struct {
			name           string
			want           bool
			confirmDeleted bool
		}{
			// FIXME: validate whether this is the behavior we want
			{name: "delete-not-confirmed", confirmDeleted: false, want: true},
			{name: "delete-confirmed", confirmDeleted: true, want: false},
		}
		for _, tt := range tests {
			t.Run(tt.name, func(t *testing.T) {
				if got := pred.Delete(event.DeleteEvent{DeleteStateUnknown: tt.confirmDeleted}); got != tt.want {
					t.Errorf("newSBRPredicate() = %v, want %v", got, tt.want)
				}
			})
		}
	})
}

func TestSBRControllerBuildGVKPredicate(t *testing.T) {
	pred := buildGVKPredicate(log.NewLog("test-log"))

	// update verifies whether only the accepted manifests trigger the reconciliation process
	t.Run("update", func(t *testing.T) {
		deploymentA := &appsv1.Deployment{}
		configMapA := &corev1.ConfigMap{
			ObjectMeta: metav1.ObjectMeta{
				Generation: 1,
			},
		}
		configMapB := &corev1.ConfigMap{
			ObjectMeta: metav1.ObjectMeta{
				Generation: 2,
			},
		}
		secretA := &corev1.Secret{
			ObjectMeta: metav1.ObjectMeta{
				Generation: 1,
			},
		}
		secretB := &corev1.Secret{
			ObjectMeta: metav1.ObjectMeta{
				Generation: 2,
			},
		}

		tests := []struct {
			name   string
			wanted bool
			a      runtime.Object
			b      runtime.Object
			metaA  metav1.Object
			metaB  metav1.Object
		}{
			{
				name:   "non supported update",
				wanted: false,
				a:      deploymentA,
				b:      deploymentA,
				metaA:  deploymentA.GetObjectMeta(),
				metaB:  deploymentA.GetObjectMeta(),
			},
			{
				name:   "supported update no changes",
				wanted: false,
				a:      configMapA,
				b:      configMapA,
				metaA:  configMapA.GetObjectMeta(),
				metaB:  configMapA.GetObjectMeta(),
			},
			{
				name:   "supported update no changes",
				wanted: false,
				a:      secretA,
				b:      secretA,
				metaA:  secretA.GetObjectMeta(),
				metaB:  secretA.GetObjectMeta(),
			},
			{
				name:   "supported update generation changed",
				wanted: true,
				a:      configMapA,
				b:      configMapB,
				metaA:  configMapA.GetObjectMeta(),
				metaB:  configMapB.GetObjectMeta(),
			},
			{
				name:   "supported update generation changed",
				wanted: true,
				a:      secretA,
				b:      secretB,
				metaA:  secretA.GetObjectMeta(),
				metaB:  secretB.GetObjectMeta(),
			},
		}
		for _, tt := range tests {
			t.Run(tt.name, func(t *testing.T) {
				e := event.UpdateEvent{
					MetaOld:   tt.metaA,
					MetaNew:   tt.metaB,
					ObjectOld: tt.a,
					ObjectNew: tt.b,
				}
				if got := pred.Update(e); got != tt.wanted {
					t.Errorf("newGVKPredicate() = %v, want %v", got, tt.wanted)
				}
			})
		}
	})
}

type fakeController struct {
	watchCallback func(src source.Source, eventhandler handler.EventHandler, predicates ...predicate.Predicate) error
}

var _ controller.Controller = (*fakeController)(nil)

func (f *fakeController) Reconcile(request reconcile.Request) (reconcile.Result, error) {
	return reconcile.Result{}, nil
}

func (f *fakeController) Start(stop <-chan struct{}) error {
	return nil
}

func (f *fakeController) Watch(src source.Source, eventhandler handler.EventHandler, predicates ...predicate.Predicate) error {
	if f.watchCallback != nil {
		return f.watchCallback(src, eventhandler, predicates...)
	}
	return nil
}

func TestSBRController_ResourceWatcher(t *testing.T) {

	controller := &sbrController{
		RestMapper: testutils.BuildTestRESTMapper(),
		logger:     log.NewLog("testSBRController"),
	}

	deploymentGVK := schema.GroupVersionKind{Kind: "Deployment", Version: "v1", Group: "apps"}
	deploymentGVR := schema.GroupVersionResource{Resource: "deployments", Version: "v1", Group: "apps"}

	t.Run("add watching for deployment GVK", func(t *testing.T) {
		ch := make(chan struct{})
		controller.Controller = &fakeController{
			watchCallback: func(src source.Source, eventhandler handler.EventHandler,
				predicates ...predicate.Predicate) error {
				kind, ok := src.(*source.Kind)
				require.True(t, ok)
				gvk := kind.Type.GetObjectKind().GroupVersionKind()
				require.Equal(t, deploymentGVK, gvk)
				close(ch)
				return nil
			},
		}
		controller.watchingGVKs = make(map[schema.GroupVersionKind]bool)
		err := controller.AddWatchForGVK(deploymentGVK)
		require.NoError(t, err)
		_, ok := controller.watchingGVKs[deploymentGVK]
		require.True(t, ok)
		<-ch
	})

	t.Run("add watching for existing deployment GVK ", func(t *testing.T) {
		err := controller.AddWatchForGVK(deploymentGVK)
		require.NoError(t, err)
	})

	t.Run("add watching for deployment GVR", func(t *testing.T) {
		controller.Controller = &fakeController{}
		controller.watchingGVKs = make(map[schema.GroupVersionKind]bool)
		err := controller.AddWatchForGVR(deploymentGVR)
		require.NoError(t, err)
		_, ok := controller.watchingGVKs[deploymentGVK]
		require.True(t, ok)
	})

	t.Run("add watching for unknown GVR", func(t *testing.T) {
		controller.Controller = &fakeController{
			watchCallback: func(src source.Source, eventhandler handler.EventHandler,
				predicates ...predicate.Predicate) error {
				panic("should not be called")
			},
		}
		controller.watchingGVKs = make(map[schema.GroupVersionKind]bool)
		gvr := schema.GroupVersionResource{Resource: "resources", Version: "v1", Group: "unknown"}
		err := controller.AddWatchForGVR(gvr)
		require.Error(t, err)
	})
}
