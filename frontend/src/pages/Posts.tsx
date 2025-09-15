import React, { useState } from 'react'
import { useDashboard } from '@/contexts/DashboardContext'
import Header from '@/components/layout/Header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Link } from 'react-router-dom'
import { 
  Plus, 
  Search,
  Eye,
  Heart,
  MessageCircle,
  Share,
  Edit,
  Trash2,
  Image,
  Video,
  FileText,
  TrendingUp,
} from 'lucide-react'
import { format } from 'date-fns'
import { it } from 'date-fns/locale'
import { formatNumber } from '@/lib/utils'

interface Post {
  id: string
  account_username: string
  account_avatar?: string
  post_type: 'feed' | 'story' | 'reel'
  content: string
  media_files: string[]
  instagram_post_id?: string
  published_at?: string
  status: 'draft' | 'published' | 'failed'
  metrics: {
    likes: number
    comments: number
    shares: number
    reach: number
    impressions: number
    engagement_rate: number
  }
  location?: string
  hashtags: string[]
  mentions: string[]
}

const Posts: React.FC = () => {
  const { accounts } = useDashboard()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [accountFilter, setAccountFilter] = useState<string>('all')

  // Mock data - in produzione verrebbe dall'API
  const mockPosts: Post[] = [
    {
      id: '1',
      account_username: accounts[0]?.username || 'account1',
      account_avatar: accounts[0]?.profile_picture_url,
      post_type: 'feed',
      content: 'Scopri la nostra nuova collezione primavera/estate! 🌸✨ Colori vivaci e tessuti leggeri per un look fresco e moderno. #fashion #spring #newcollection',
      media_files: ['image1.jpg', 'image2.jpg'],
      instagram_post_id: 'ABC123',
      published_at: new Date(Date.now() - 86400000).toISOString(),
      status: 'published',
      metrics: {
        likes: 1247,
        comments: 89,
        shares: 23,
        reach: 5420,
        impressions: 8730,
        engagement_rate: 4.2
      },
      location: 'Milano, Italy',
      hashtags: ['fashion', 'spring', 'newcollection'],
      mentions: []
    },
    {
      id: '2',
      account_username: accounts[0]?.username || 'account1',
      account_avatar: accounts[0]?.profile_picture_url,
      post_type: 'story',
      content: 'Behind the scenes del nostro shooting! 📸',
      media_files: ['video1.mp4'],
      published_at: new Date(Date.now() - 3600000).toISOString(),
      status: 'published',
      metrics: {
        likes: 0,
        comments: 0,
        shares: 0,
        reach: 2100,
        impressions: 2450,
        engagement_rate: 0
      },
      hashtags: ['bts', 'shooting'],
      mentions: []
    },
    {
      id: '3',
      account_username: accounts[1]?.username || 'account2',
      account_avatar: accounts[1]?.profile_picture_url,
      post_type: 'reel',
      content: 'Tutorial veloce: come abbinare i nostri accessori! 💫 Quale combinazione preferite?',
      media_files: ['reel1.mp4'],
      instagram_post_id: 'DEF456',
      published_at: new Date(Date.now() - 172800000).toISOString(),
      status: 'published',
      metrics: {
        likes: 3240,
        comments: 156,
        shares: 89,
        reach: 12500,
        impressions: 18900,
        engagement_rate: 6.8
      },
      hashtags: ['tutorial', 'accessories', 'style'],
      mentions: []
    },
    {
      id: '4',
      account_username: accounts[0]?.username || 'account1',
      post_type: 'feed',
      content: 'Nuovo post in lavorazione... Cosa ne pensate di questo concept? 🤔',
      media_files: ['draft1.jpg'],
      status: 'draft',
      metrics: {
        likes: 0,
        comments: 0,
        shares: 0,
        reach: 0,
        impressions: 0,
        engagement_rate: 0
      },
      hashtags: ['wip', 'concept'],
      mentions: []
    }
  ]

  const getPostTypeIcon = (type: string) => {
    switch (type) {
      case 'story':
        return <Image className="h-4 w-4" />
      case 'reel':
        return <Video className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'published':
        return <Badge className="bg-green-100 text-green-800">Pubblicato</Badge>
      case 'failed':
        return <Badge variant="destructive">Fallito</Badge>
      default:
        return <Badge variant="secondary">Bozza</Badge>
    }
  }

  const filteredPosts = mockPosts.filter(post => {
    const matchesSearch = post.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.hashtags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesStatus = statusFilter === 'all' || post.status === statusFilter
    const matchesType = typeFilter === 'all' || post.post_type === typeFilter
    const matchesAccount = accountFilter === 'all' || post.account_username === accountFilter
    
    return matchesSearch && matchesStatus && matchesType && matchesAccount
  })

  const handleDeletePost = async (postId: string) => {
    // Implementazione eliminazione post
    console.log('Eliminazione post:', postId)
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <Header />
      
      {/* Header sezione */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Post</h1>
          <p className="text-muted-foreground">
            Gestisci i tuoi contenuti Instagram
          </p>
        </div>
        <Button asChild>
          <Link to="/posts/new">
            <Plus className="mr-2 h-4 w-4" />
            Nuovo Post
          </Link>
        </Button>
      </div>

      {/* Statistiche */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Post Totali</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockPosts.length}</div>
            <p className="text-xs text-muted-foreground">
              {mockPosts.filter(p => p.status === 'published').length} pubblicati
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Likes Totali</CardTitle>
            <Heart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(mockPosts.reduce((sum, post) => sum + post.metrics.likes, 0))}
            </div>
            <p className="text-xs text-muted-foreground">
              Media: {Math.round(mockPosts.reduce((sum, post) => sum + post.metrics.likes, 0) / mockPosts.length)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Engagement Medio</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(mockPosts.reduce((sum, post) => sum + post.metrics.engagement_rate, 0) / mockPosts.length).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Tutti i post pubblicati
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Reach Totale</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(mockPosts.reduce((sum, post) => sum + post.metrics.reach, 0))}
            </div>
            <p className="text-xs text-muted-foreground">
              Utenti raggiunti
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filtri */}
      <Card>
        <CardHeader>
          <CardTitle>Filtri</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Cerca nei contenuti..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Stato" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tutti gli stati</SelectItem>
                <SelectItem value="published">Pubblicati</SelectItem>
                <SelectItem value="draft">Bozze</SelectItem>
                <SelectItem value="failed">Falliti</SelectItem>
              </SelectContent>
            </Select>

            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="Tipo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tutti i tipi</SelectItem>
                <SelectItem value="feed">Feed</SelectItem>
                <SelectItem value="story">Story</SelectItem>
                <SelectItem value="reel">Reel</SelectItem>
              </SelectContent>
            </Select>

            {accounts.length > 1 && (
              <Select value={accountFilter} onValueChange={setAccountFilter}>
                <SelectTrigger className="w-[160px]">
                  <SelectValue placeholder="Account" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tutti gli account</SelectItem>
                  {accounts.map(account => (
                    <SelectItem key={account.id} value={account.username}>
                      @{account.username}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Lista post */}
      <div className="grid gap-6">
        {filteredPosts.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">Nessun post trovato</h3>
              <p className="text-muted-foreground mb-4 text-center">
                {searchTerm || statusFilter !== 'all' || typeFilter !== 'all' || accountFilter !== 'all'
                  ? 'Nessun post corrisponde ai filtri selezionati'
                  : 'Non hai ancora creato nessun post'
                }
              </p>
              {!searchTerm && statusFilter === 'all' && typeFilter === 'all' && accountFilter === 'all' && (
                <Button asChild>
                  <Link to="/posts/new">
                    <Plus className="mr-2 h-4 w-4" />
                    Crea il tuo primo post
                  </Link>
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          filteredPosts.map((post) => (
            <Card key={post.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={post.account_avatar} />
                      <AvatarFallback>
                        {post.account_username.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    
                    <div>
                      <div className="flex items-center space-x-2 mb-1">
                        <CardTitle className="text-lg">@{post.account_username}</CardTitle>
                        <div className="flex items-center space-x-1">
                          {getPostTypeIcon(post.post_type)}
                          <span className="text-sm text-muted-foreground capitalize">
                            {post.post_type}
                          </span>
                        </div>
                        {getStatusBadge(post.status)}
                      </div>
                      
                      {post.published_at && (
                        <p className="text-sm text-muted-foreground">
                          Pubblicato {format(new Date(post.published_at), 'dd MMM yyyy, HH:mm', { locale: it })}
                        </p>
                      )}
                      
                      {post.location && (
                        <p className="text-xs text-muted-foreground mt-1">
                          📍 {post.location}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" asChild>
                      <Link to={`/posts/${post.id}`}>
                        <Eye className="h-4 w-4" />
                      </Link>
                    </Button>
                    
                    <Button variant="outline" size="sm" asChild>
                      <Link to={`/posts/${post.id}/edit`}>
                        <Edit className="h-4 w-4" />
                      </Link>
                    </Button>

                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="outline" size="sm" className="text-destructive hover:text-destructive">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Elimina Post</AlertDialogTitle>
                          <AlertDialogDescription>
                            Sei sicuro di voler eliminare questo post? Questa azione non può essere annullata.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Annulla</AlertDialogCancel>
                          <AlertDialogAction
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            onClick={() => handleDeletePost(post.id)}
                          >
                            Elimina
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
              </CardHeader>

              <CardContent>
                <div className="space-y-4">
                  {/* Contenuto */}
                  <div>
                    <p className="text-sm mb-2">{post.content}</p>
                    
                    {/* Hashtags */}
                    {post.hashtags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {post.hashtags.map((tag, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            #{tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                    
                    {/* Media info */}
                    {post.media_files.length > 0 && (
                      <p className="text-xs text-muted-foreground">
                        📎 {post.media_files.length} file media allegati
                      </p>
                    )}
                  </div>

                  {/* Metriche (solo per post pubblicati) */}
                  {post.status === 'published' && (
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 pt-4 border-t">
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1 mb-1">
                          <Heart className="h-4 w-4 text-red-500" />
                          <span className="font-medium">{formatNumber(post.metrics.likes)}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">Likes</p>
                      </div>
                      
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1 mb-1">
                          <MessageCircle className="h-4 w-4 text-blue-500" />
                          <span className="font-medium">{formatNumber(post.metrics.comments)}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">Commenti</p>
                      </div>
                      
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1 mb-1">
                          <Share className="h-4 w-4 text-green-500" />
                          <span className="font-medium">{formatNumber(post.metrics.shares)}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">Condivisioni</p>
                      </div>
                      
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1 mb-1">
                          <Eye className="h-4 w-4 text-purple-500" />
                          <span className="font-medium">{formatNumber(post.metrics.reach)}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">Reach</p>
                      </div>
                      
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1 mb-1">
                          <TrendingUp className="h-4 w-4 text-orange-500" />
                          <span className="font-medium">{formatNumber(post.metrics.impressions)}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">Impressioni</p>
                      </div>
                      
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1 mb-1">
                          <span className="font-medium">{post.metrics.engagement_rate.toFixed(1)}%</span>
                        </div>
                        <p className="text-xs text-muted-foreground">Engagement</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

export default Posts
